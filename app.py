from flask import Flask, request, jsonify, send_from_directory, Response
import os
import hashlib
import subprocess
import logging
from shared import app
from blueprints.routes import blueprint
from werkzeug.utils import secure_filename
import json

app.register_blueprint(blueprint)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Setup directories
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 5000

os.makedirs(FILE_DIR, exist_ok=True)
os.makedirs(TORRENT_DIR, exist_ok=True)

# Torrent trackers to be used for distribution
TRACKER_URLS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "http://tracker.opentrackr.org:1337/announce",
    "udp://open.tracker.cl:1337/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker-udp.gbitt.info:80/announce",
    "udp://explodie.org:6969/announce",
    "udp://exodus.desync.com:6969/announce",
    # ... add the rest of the provided trackers here ...
]

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_magnet_link(info_hash, file_name):
    """Generate a magnet link using the provided trackers and info hash."""
    trackers = "&".join([f"tr={urllib.parse.quote(tracker)}" for tracker in TRACKER_URLS])
    magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(file_name)}&{trackers}"
    return magnet_link

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle the image upload, create a torrent, and return the magnet link."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(FILE_DIR, filename)
        file.save(file_path)
        logging.info(f"File saved to {file_path}")

        # Create torrent and start seeding with WebTorrent CLI
        try:
            torrent_file_path = os.path.join(TORRENT_DIR, f"{filename}.torrent")

            # Create the torrent file using webtorrent CLI
            tracker_list = " ".join([f"--announce={tracker}" for tracker in TRACKER_URLS])
            cmd = f"webtorrent create '{file_path}' {tracker_list} -o '{torrent_file_path}'"
            logging.info(f"Running command: {cmd}")
            subprocess.run(cmd, shell=True, check=True)

            # Extract info hash from the torrent file
            torrent_info_cmd = f"webtorrent info '{torrent_file_path}'"
            logging.info(f"Getting torrent info with command: {torrent_info_cmd}")
            result = subprocess.run(torrent_info_cmd, shell=True, check=True, capture_output=True, text=True)
            torrent_info = json.loads(result.stdout)

            # Start seeding the file
            seed_cmd = f"webtorrent seed '{file_path}' {tracker_list}"
            logging.info(f"Seeding with command: {seed_cmd}")
            subprocess.Popen(seed_cmd, shell=True)

            # Generate magnet link
            info_hash = torrent_info['infoHash']
            magnet_url = generate_magnet_link(info_hash, filename)
            logging.info(f"Magnet URL generated: {magnet_url}")

            return jsonify({"magnet_url": magnet_url}), 200

        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating or seeding torrent: {e}")
            return jsonify({"error": "Error creating or seeding torrent"}), 500

    return jsonify({"error": "Invalid file type"}), 400

@app.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve the uploaded image."""
    return send_from_directory(FILE_DIR, filename)

if __name__ == "__main__":
    logging.info("Starting webseed server")
    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
