from flask import Flask, request, jsonify, send_file, Response
import os
import hashlib
import threading
import struct
import socket
import logging
from shared import app
import time
from werkzeug.utils import secure_filename
import json
from blueprints.routes import blueprint

app.register_blueprint(blueprint)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Setup directories and Flask app
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 6969

os.makedirs(FILE_DIR, exist_ok=True)
os.makedirs(TORRENT_DIR, exist_ok=True)

active_peers = {}  # Structure: {info_hash: {peer_id: {ip, port, uploaded, downloaded, left}}}
seeding = {}
torrent_info_cache = {}  # Cache to store torrent info metadata for serving to clients

# Bencode encoding function
def bencode(value):
    if isinstance(value, int):
        return f"i{value}e".encode()
    elif isinstance(value, bytes):
        return f"{len(value)}:".encode() + value
    elif isinstance(value, str):
        return bencode(value.encode())
    elif isinstance(value, list):
        return b"l" + b"".join(bencode(i) for i in value) + b"e"
    elif isinstance(value, dict):
        return b"d" + b"".join(bencode(k) + bencode(v) for k, v in sorted(value.items())) + b"e"
    else:
        raise TypeError("Unsupported type")

# Generate SHA1 Hashes for File Pieces
def generate_pieces(file_path, piece_length=524288):
    pieces = b""
    with open(file_path, "rb") as f:
        while True:
            piece = f.read(piece_length)
            if not piece:
                break
            pieces += hashlib.sha1(piece).digest()
    logging.debug(f"Generated pieces hash: {pieces}")
    return pieces

def create_torrent_file(file_path, filename):
    logging.debug(f"Creating torrent file for {filename}")
    torrent_file_path = os.path.join(TORRENT_DIR, f"{filename}.torrent")
    file_length = os.path.getsize(file_path)
    pieces = generate_pieces(file_path)
    
    info = {
        "name": filename,
        "piece length": 524288,
        "pieces": pieces,
        "length": file_length
    }
    
    # Including the web seed URL
    torrent = {
        "announce": f"http://{request.host}/announce",
        "info": info,
        "url-list": [f"http://{request.host}/static/{filename}"]  # Web seeding URL
    }
    
    # Cache the info dictionary using the info_hash for quick lookup
    info_hash = hashlib.sha1(bencode(info)).hexdigest()
    logging.debug(f"Info hash: {info_hash}")
    torrent_info_cache[info_hash] = info

    with open(torrent_file_path, "wb") as f:
        f.write(bencode(torrent))
    
    logging.debug(f"Torrent file created at {torrent_file_path}")
    return torrent_file_path

# Magnet Link Generation
def generate_magnet_link(filename, torrent_file_path):
    logging.debug(f"Generating magnet link for {filename}")
    with open(torrent_file_path, 'rb') as f:
        torrent_data = f.read()
        info_hash = hashlib.sha1(torrent_data).hexdigest()
        web_seed_url = f"http://{request.host}/static/{filename}"
        magnet_link = (
            f"magnet:?xt=urn:btih:{info_hash}&dn={filename}"
            f"&tr=http://{request.host}/announce&ws={web_seed_url}"
        )
        logging.debug(f"Magnet link: {magnet_link}")
        return magnet_link

def stop_seeding_and_delete_file(info_hash):
    logging.debug(f"Delaying the stop of web seeding for {info_hash} for 10 minutes to ensure proper seeding.")
    time.sleep(600)  # Wait for 10 minutes before stopping web seeding
    if info_hash in seeding and not seeding[info_hash]:
        filename = next((f for f, h in torrent_info_cache.items() if hashlib.sha1(bencode(h)).hexdigest() == info_hash), None)
        if filename:
            torrent_file_path = os.path.join(TORRENT_DIR, f"{filename}.torrent")
            file_path = os.path.join(FILE_DIR, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.debug(f"File {filename} removed from server")
            
            if os.path.exists(torrent_file_path):
                os.remove(torrent_file_path)
                logging.debug(f"Torrent {filename} removed from server")

@app.route('/announce', methods=['GET'])
def announce():
    global active_peers, seeding

    logging.debug("Received announce request")
    
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')
    ip = request.remote_addr
    port = int(request.args.get('port', 6881))
    uploaded = int(request.args.get('uploaded', 0))
    downloaded = int(request.args.get('downloaded', 0))
    left = int(request.args.get('left', 0))
    event = request.args.get('event')
    numwant = int(request.args.get('numwant', 50))  # Number of peers client wants

    logging.debug(f"info_hash: {info_hash}, peer_id: {peer_id}, ip: {ip}, port: {port}, event: {event}, numwant: {numwant}")
    
    if not info_hash or not peer_id:
        logging.error("Missing info_hash or peer_id")
        return "Missing info_hash or peer_id", 400
    
    if info_hash not in active_peers:
        active_peers[info_hash] = {}
        seeding[info_hash] = True
        logging.debug(f"New info_hash {info_hash} added to active_peers")

    if event == 'started' or peer_id not in active_peers[info_hash]:
        active_peers[info_hash][peer_id] = {
            'ip': ip,
            'port': port,
            'uploaded': uploaded,
            'downloaded': downloaded,
            'left': left
        }
        logging.debug(f"Peer {peer_id} started or added to active_peers")
    elif event == 'stopped':
        if peer_id in active_peers[info_hash]:
            del active_peers[info_hash][peer_id]
            logging.debug(f"Peer {peer_id} stopped and removed from active_peers")
    elif event == 'completed':
        logging.debug(f"Peer {peer_id} completed download")

    # If peers start seeding, stop web seeding
    # Web seeding should stop only if a complete peer is found
    if len(active_peers[info_hash]) > 1:
        complete_peers = [p for p in active_peers[info_hash].values() if p['left'] == 0]
        if complete_peers:
            seeding[info_hash] = False
            logging.debug(f"Complete peer found for {info_hash}, stopping web seeding")
            threading.Thread(target=stop_seeding_and_delete_file, args=(info_hash,)).start()
        else:
            logging.debug(f"No complete peers yet for {info_hash}, continuing web seeding")
    
    # Avoid duplicate peer entries
    peers = list({f"{p['ip']}:{p['port']}": p for p in active_peers[info_hash].values()}.values())
    
    # Add the server peer
    try:
        server_ip = socket.gethostbyname('gremlin.codes')
        server_peer = {
            'ip': server_ip,
            'port': 5000
        }
        peers.append(server_peer)
        logging.debug(f"Server peer added: {server_peer}")
    except socket.gaierror as e:
        logging.error(f"Error resolving gremlin.codes: {e}")
    
    # Return the non-compact peer list
    return jsonify({
        'interval': 1800,
        'peers': [{'ip': peer['ip'], 'port': peer['port']} for peer in peers]
    })


# Scrape URL Handling
@app.route('/scrape', methods=['GET'])
def scrape():
    global active_peers, seeding
    
    logging.debug("Received scrape request")
    
    info_hash = request.args.get('info_hash')
    
    if not info_hash:
        logging.error("Info hash not provided")
        return "Info hash not provided", 400
    
    # Respond with the number of seeders and leechers
    num_seeders = sum(1 for peer in active_peers.get(info_hash, {}).values() if peer['left'] == 0)
    num_leechers = sum(1 for peer in active_peers.get(info_hash, {}).values() if peer['left'] > 0)
    
    scrape_response = {
        'files': {
            info_hash: {
                'complete': num_seeders,
                'incomplete': num_leechers,
                'downloaded': 0  # Total number of times the file has been downloaded
            }
        }
    }
    
    logging.debug(f"Scrape response: {scrape_response}")
    return jsonify(scrape_response)


# File Upload Handling
@app.route('/upload', methods=['POST'])
def upload_file():
    logging.debug("Received file upload request")
    
    if 'file' not in request.files:
        logging.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        logging.debug(f"File {filename} received for upload")
        file_path = os.path.join(FILE_DIR, filename)
        file.save(file_path)
        logging.debug(f"File saved at {file_path}")

        torrent_file_path = create_torrent_file(file_path, filename)
        magnet_url = generate_magnet_link(filename, torrent_file_path)
        return jsonify({"magnetUrl": magnet_url})

    logging.error("Unknown error occurred during file upload")
    return jsonify({"error": "Unknown error occurred"}), 500

# Serving Static Files
@app.route('/static/<filename>')
def serve_file(filename):
    logging.debug(f"Serving static file {filename}")
    file_path = os.path.join(FILE_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    logging.error(f"File {filename} not found")
    return "File not found", 404


if __name__ == "__main__":
    logging.debug("Starting tracker server")
    app.run(host="0.0.0.0", port=5000, debug=True)
