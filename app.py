from flask import Flask, request, Response
import os
import logging
import socket
import struct
import threading
from bencode import encode
from urllib.parse import unquote_to_bytes

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Setup directories and Flask app
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 5000

os.makedirs(FILE_DIR, exist_ok=True)
os.makedirs(TORRENT_DIR, exist_ok=True)

active_peers = {}  # Structure: {info_hash: {peer_id: {ip, port, uploaded, downloaded, left}}}
seeding = {}
interval = 1800

def decode_request(path):
    """ Return the decoded request string. """
    # Strip off the start characters
    path = path.lstrip("/?")
    return dict(request.args)

def add_peer(info_hash, peer_id, ip, port):
    """ Add the peer to the torrent database. """
    # If we've heard of this, just add the peer
    if info_hash in active_peers:
        if (peer_id, ip, port) not in active_peers[info_hash]:
            active_peers[info_hash].append((peer_id, ip, port))
    # Otherwise, add the info_hash and the peer
    else:
        active_peers[info_hash] = [(peer_id, ip, port)]

def make_compact_peer_list(peer_list):
    """ Return a compact peer string, given a list of peer details. """
    peer_string = b""
    for peer in peer_list:
        ip = socket.inet_aton(peer[1])
        port = struct.pack(">H", int(peer[2]))
        peer_string += ip + port
    return peer_string

def make_peer_list(peer_list):
    """ Return an expanded peer list suitable for the client, given the peer list. """
    peers = []
    for peer in peer_list:
        p = {"peer id": peer[0], "ip": peer[1], "port": int(peer[2])}
        peers.append(p)
    return peers

@app.route('/announce', methods=['GET'])
def announce():
    logging.debug("Received announce request")

    package = decode_request(request.path)
    
    if not package:
        return Response(status=400)

    info_hash = unquote_to_bytes(package["info_hash"])
    compact = bool(int(package.get("compact", 0)))
    ip = request.remote_addr
    port = package["port"]
    peer_id = package["peer_id"]
    event = package.get("event")

    add_peer(info_hash, peer_id, ip, port)

    if event == 'stopped':
        if info_hash in active_peers:
            active_peers[info_hash] = [p for p in active_peers[info_hash] if p[0] != peer_id]

    response = {
        "interval": interval,
        "complete": sum(1 for peer in active_peers[info_hash] if peer[2] == 0),
        "incomplete": sum(1 for peer in active_peers[info_hash] if peer[2] > 0),
        "peers": make_compact_peer_list(active_peers[info_hash]) if compact else make_peer_list(active_peers[info_hash])
    }

    return Response(encode(response), content_type="text/plain")

@app.route('/scrape', methods=['GET'])
def scrape():
    logging.debug("Received scrape request")
    
    package = decode_request(request.path)
    
    if not package or "info_hash" not in package:
        return Response(status=400)

    info_hash = unquote_to_bytes(package["info_hash"])

    response = {
        "files": {
            info_hash: {
                "complete": sum(1 for peer in active_peers.get(info_hash, []) if peer[2] == 0),
                "incomplete": sum(1 for peer in active_peers.get(info_hash, []) if peer[2] > 0),
                "downloaded": 0
            }
        }
    }

    return Response(encode(response), content_type="text/plain")

if __name__ == "__main__":
    logging.debug("Starting tracker server")
    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
