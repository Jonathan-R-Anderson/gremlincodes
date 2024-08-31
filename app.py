from shared import app
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
from qbittorrent import Client
from flask import Flask, send_file, request, jsonify, render_template
import os
import threading
import time
import subprocess
from werkzeug.utils import secure_filename

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

# Base directory for static files
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'  # Directory for storing .torrent files

# Ensure the directory for .torrent files exists
os.makedirs(TORRENT_DIR, exist_ok=True)

# Initialize qBittorrent client
client = Client('http://127.0.0.1:8080/')
client.login('admin', 'admin')

# Dictionary to track the number of active peers per file
active_peers = {}
seeding = {}

@app.route('/<filename>')
def serve_file(filename):
    file_path = os.path.join(FILE_DIR, filename)
    torrent_path = os.path.join(TORRENT_DIR, filename.replace('.zip', '.torrent'))

    if os.path.exists(file_path):
        return send_file(file_path)
    elif os.path.exists(torrent_path):
        return send_file(torrent_path)
    else:
        return "File not found", 404

@app.route('/announce', methods=['GET'])
def announce():
    global active_peers, seeding

    filename = request.args.get('filename')
    event = request.args.get('event')

    if not filename:
        return "Filename not provided", 400

    if filename not in active_peers:
        active_peers[filename] = 0
        seeding[filename] = True

    if event == 'started':
        active_peers[filename] += 1
    elif event == 'stopped':
        active_peers[filename] -= 1

    if active_peers[filename] > 1 and seeding[filename]:
        seeding[filename] = False
        threading.Thread(target=drop_file_after_delay, args=(filename,)).start()

    return jsonify({"peers": active_peers[filename]})

def drop_file_after_delay(filename):
    time.sleep(60)  # Wait for 1 minute before dropping the file
    if active_peers[filename] > 1:
        file_path = os.path.join(FILE_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {filename} dropped from the server")

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

        # Create and seed the .torrent file
        torrent_file_path = create_torrent_file(file_path, filename)
        magnet_url = start_seeding(torrent_file_path)
        return jsonify({"magnetUrl": magnet_url})

    return jsonify({"error": "Unknown error occurred"}), 500

def create_torrent_file(file_path, filename):
    torrent_file_path = os.path.join(TORRENT_DIR, f"{filename}.torrent")

    # Remove the existing .torrent file if it exists
    if os.path.exists(torrent_file_path):
        os.remove(torrent_file_path)

    # Create the .torrent file using mktorrent command
    command = [
        "mktorrent",
        "-o", torrent_file_path,
        "-a", "http://127.0.0.1:8080/announce",
        file_path
    ]

    # Run the command
    subprocess.run(command, check=True)

    return torrent_file_path


def start_seeding(torrent_file_path):
    # Add the .torrent file to the qBittorrent client for seeding
    with open(torrent_file_path, 'rb') as f:
        torrent_content = f.read()
        client.add_torrent(torrent_content)  # Using add_torrent

    # Get the magnet link for the torrent
    torrents = client.torrents()  # Get the list of torrents
    magnet_url = None
    for t in torrents:
        if t['name'] == os.path.basename(torrent_file_path).replace('.torrent', ''):
            magnet_url = t['magnet_uri']
            break

    # Function to drop the file after some peers are seeding
    def drop_file():
        time.sleep(60)  # Wait for 1 minute
        if os.path.exists(torrent_file_path):
            os.remove(torrent_file_path)

    threading.Thread(target=drop_file).start()
    return magnet_url if magnet_url else "Magnet link not found"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
