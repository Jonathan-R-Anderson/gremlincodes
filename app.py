import os
import subprocess
import logging
import threading
import time
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import json
import urllib
from shared import app
from blueprints import blueprint


app.register_blueprint(blueprint)


# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Setup directories
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 5000
SEED_FILE = 'seeded_files.json'

os.makedirs(FILE_DIR, exist_ok=True)
os.makedirs(TORRENT_DIR, exist_ok=True)

# Torrent WSS trackers to be used for distribution (updated for WebSockets)
TRACKER_URLS = [
    "wss://tracker.openwebtorrent.com",
    "wss://tracker.btorrent.xyz",
    "wss://tracker.fastcast.nz",
    "wss://tracker.webtorrent.io"
]

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Dictionary to store magnet URLs for seeding files
seeded_files = {}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def seed_file(file_path):
    """Function to seed the file using the WebTorrent command."""
    try:
        # Prepare tracker list for WebTorrent seed command
        tracker_list = " ".join([f"--announce={tracker}" for tracker in TRACKER_URLS])
        
        # WebTorrent seed command with trackers and keep-seeding
        cmd = f"webtorrent seed '{file_path}' {tracker_list} --keep-seeding"
        logging.info(f"Running seeding command: {cmd}")

        # Run the command in a subprocess
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        magnet_url = None

        # Read output to extract magnet link
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break

            if output:
                logging.info(f"WebTorrent output: {output.strip()}")
                if "Magnet URI:" in output:
                    magnet_url = output.split("Magnet URI:")[1].strip()
                    seeded_files[file_path] = magnet_url
                    logging.info(f"Magnet URL found: {magnet_url}")

        # Ensure subprocess completes
        process.communicate()

        if process.returncode != 0:
            logging.error(f"Seeding process failed for {file_path}")

    except Exception as e:
        logging.error(f"Error while seeding file: {str(e)}")

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle the image upload, start torrent seeding in a separate thread, and return the magnet link."""
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

        try:
            # Start seeding in a separate thread
            seed_thread = threading.Thread(target=seed_file, args=(file_path,))
            seed_thread.start()

            # Poll the seeded_files dictionary until the magnet URL is available
            max_wait_time = 10  # Max wait time in seconds
            wait_time = 0
            while file_path not in seeded_files and wait_time < max_wait_time:
                time.sleep(0.5)  # Sleep for 500ms
                wait_time += 0.5

            if file_path in seeded_files:
                magnet_url = seeded_files[file_path]
                logging.info(f"Magnet URL generated: {magnet_url}")
                return jsonify({"magnet_url": magnet_url}), 200
            else:
                return jsonify({"error": "Failed to generate magnet URL in time"}), 500

        except Exception as e:
            logging.error(f"Error during seeding: {e}")
            return jsonify({"error": "Error creating torrent", "details": str(e)}), 500

    return jsonify({"error": "Invalid file type"}), 400

@app.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve the uploaded image."""
    return send_from_directory(FILE_DIR, filename)

if __name__ == "__main__":
    logging.info("Starting webseed server")
    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
