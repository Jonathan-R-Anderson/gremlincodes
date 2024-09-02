from flask import Flask, request, Response
import os
import logging
import socket
import struct
from threading import Thread, Timer
from collections import defaultdict
import json
import time
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

active_peers = defaultdict(list)  # Structure: {info_hash: [(peer_id, ip, port, uploaded, downloaded, left)]}
send_freq_list = defaultdict(int)
has_informed_tracker = defaultdict(bool)
interval = 1800

class Tracker:
    def __init__(self):
        self.tracker_socket = self.set_socket(TRACKER_PORT)
        self.file_owners_list = defaultdict(list)
        self.send_freq_list = defaultdict(int)
        self.has_informed_tracker = defaultdict(bool)

    def set_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", port))
        return sock

    def add_peer(self, info_hash, peer_id, ip, port, uploaded, downloaded, left):
        peer_info = (peer_id, ip, port, uploaded, downloaded, left)
        if info_hash in active_peers:
            if peer_info not in active_peers[info_hash]:
                active_peers[info_hash].append(peer_info)
        else:
            active_peers[info_hash] = [peer_info]
        self.send_freq_list[peer_id] += 1

    def remove_peer(self, info_hash, peer_id):
        if info_hash in active_peers:
            active_peers[info_hash] = [p for p in active_peers[info_hash] if p[0] != peer_id]
            if not active_peers[info_hash]:
                del active_peers[info_hash]

    def make_compact_peer_list(self, peer_list):
        peer_string = b""
        for peer in peer_list:
            ip = socket.inet_aton(peer[1])
            port = struct.pack(">H", int(peer[2]))
            peer_string += ip + port
        return peer_string

    def make_peer_list(self, peer_list):
        peers = []
        for peer in peer_list:
            p = {"peer id": peer[0], "ip": peer[1], "port": int(peer[2])}
            peers.append(p)
        return peers

    def save_db_as_json(self):
        if not os.path.exists(TORRENT_DIR):
            os.makedirs(TORRENT_DIR)

        nodes_info_path = os.path.join(TORRENT_DIR, "nodes.json")
        files_info_path = os.path.join(TORRENT_DIR, "files.json")

        with open(nodes_info_path, 'w') as nodes_json:
            json.dump(self.send_freq_list, nodes_json, indent=4, sort_keys=True)

        with open(files_info_path, 'w') as files_json:
            json.dump(self.file_owners_list, files_json, indent=4, sort_keys=True)

    def check_nodes_periodically(self, interval):
        global next_call
        alive_nodes_ids = set()
        dead_nodes_ids = set()
        try:
            for node, has_informed in self.has_informed_tracker.items():
                node_id, node_addr = node[0], node[1]
                if has_informed:
                    self.has_informed_tracker[node] = False
                    alive_nodes_ids.add(node_id)
                else:
                    dead_nodes_ids.add(node_id)
                    self.remove_peer(node_id=node_id, addr=node_addr)
        except RuntimeError:
            pass

        if alive_nodes_ids or dead_nodes_ids:
            log_content = f"Node(s) {list(alive_nodes_ids)} is in the torrent and node(s) {list(dead_nodes_ids)} have left."
            logging.debug(log_content)

        next_call = next_call + interval
        Timer(next_call - time.time(), self.check_nodes_periodically, args=(interval,)).start()

    def listen(self):
        timer_thread = Thread(target=self.check_nodes_periodically, args=(interval,))
        timer_thread.setDaemon(True)
        timer_thread.start()

        while True:
            data, addr = self.tracker_socket.recvfrom(8192)  # Adjust buffer size if necessary
            t = Thread(target=self.handle_node_request, args=(data, addr))
            t.start()

    def run(self):
        log_content = f"***************** Tracker program started just right now! *****************"
        logging.debug(log_content)
        t = Thread(target=self.listen)
        t.daemon = True
        t.start()
        t.join()

tracker = Tracker()

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
    uploaded = int(package.get("uploaded", 0))
    downloaded = int(package.get("downloaded", 0))
    left = int(package.get("left", 0))
    event = package.get("event")

    tracker.add_peer(info_hash, peer_id, ip, port, uploaded, downloaded, left)

    if event == 'stopped':
        tracker.remove_peer(info_hash, peer_id)

    response = {
        "interval": interval,
        "complete": sum(1 for peer in active_peers[info_hash] if peer[5] == 0),
        "incomplete": sum(1 for peer in active_peers[info_hash] if peer[5] > 0),
        "peers": tracker.make_compact_peer_list(active_peers[info_hash]) if compact else tracker.make_peer_list(active_peers[info_hash])
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
                "complete": sum(1 for peer in active_peers.get(info_hash, []) if peer[5] == 0),
                "incomplete": sum(1 for peer in active_peers.get(info_hash, []) if peer[5] > 0),
                "downloaded": 0
            }
        }
    }

    return Response(encode(response), content_type="text/plain")

if __name__ == "__main__":
    logging.debug("Starting tracker server")
    tracker.run()
    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
