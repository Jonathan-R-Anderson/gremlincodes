from flask import Flask, request, jsonify, send_file, render_template
import os
import hashlib
import threading
from shared import app, gremlinThreadABI, gremlinThreadAddress
import time
from werkzeug.utils import secure_filename
import json

# Setup directories and Flask app
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 6969

os.makedirs(FILE_DIR, exist_ok=True)
os.makedirs(TORRENT_DIR, exist_ok=True)

active_peers = {}
seeding = {}

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
    return pieces

# Create Torrent File
def create_torrent_file(file_path, filename):
    torrent_file_path = os.path.join(TORRENT_DIR, f"{filename}.torrent")
    file_length = os.path.getsize(file_path)
    pieces = generate_pieces(file_path)
    
    info = {
        "name": filename,
        "piece length": 524288,
        "pieces": pieces,
        "length": file_length
    }
    
    torrent = {
        "announce": f"http://{request.host}/announce",
        "info": info,
        "url-list": [f"http://{request.host}/static/{filename}"]  # Web seeding URL
    }
    
    with open(torrent_file_path, "wb") as f:
        f.write(bencode(torrent))
    
    return torrent_file_path

# Magnet Link Generation
def generate_magnet_link(filename, torrent_file_path):
    with open(torrent_file_path, 'rb') as f:
        torrent_data = f.read()
        info_hash = hashlib.sha1(torrent_data).hexdigest()
        magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={filename}&tr=http://{request.host}/announce"
        return magnet_link

# Announce URL Handling
@app.route('/announce', methods=['GET'])
def announce():
    global active_peers, seeding
    
    info_hash = request.args.get('info_hash')
    event = request.args.get('event')
    
    if not info_hash:
        return "Info hash not provided", 400
    
    if info_hash not in active_peers:
        active_peers[info_hash] = 0
        seeding[info_hash] = True
    
    if event == 'started':
        active_peers[info_hash] += 1
    elif event == 'stopped':
        active_peers[info_hash] -= 1
    
    # If peers start seeding, stop web seeding
    if active_peers[info_hash] > 1 and seeding[info_hash]:
        seeding[info_hash] = False
        threading.Thread(target=stop_seeding_and_delete_file, args=(info_hash,)).start()
    
    return jsonify({"peers": active_peers[info_hash]})

# Stop Seeding and Delete File
def stop_seeding_and_delete_file(info_hash):
    time.sleep(60)
    for filename, _ in seeding.items():
        torrent_file_path = os.path.join(TORRENT_DIR, f"{filename}.torrent")
        file_path = os.path.join(FILE_DIR, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {filename} removed from server")
        
        if os.path.exists(torrent_file_path):
            os.remove(torrent_file_path)
            print(f"Torrent {filename} removed from server")

# File Upload Handling
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(FILE_DIR, filename)
        file.save(file_path)

        torrent_file_path = create_torrent_file(file_path, filename)
        magnet_url = generate_magnet_link(filename, torrent_file_path)
        return jsonify({"magnetUrl": magnet_url})

    return jsonify({"error": "Unknown error occurred"}), 500

# Serving Static Files
@app.route('/static/<filename>')
def serve_file(filename):
    file_path = os.path.join(FILE_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return "File not found", 404

@app.route('/')
def index():
    return render_template('index.html', gremlinThreadABI=json.dumps(gremlinThreadABI), gremlinThreadAddress=gremlinThreadAddress)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
