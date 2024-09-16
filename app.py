from flask import Flask, request, jsonify, send_from_directory, Response
import os
import subprocess
import logging
import threading
import time
from shared import app
from blueprints.routes import blueprint
from werkzeug.utils import secure_filename
import json
import urllib

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
]

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Dictionary to store magnet URLs for seeding files
seeded_files = {}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_magnet_link(info_hash, file_name):
    """Generate a magnet link using the provided trackers and info hash."""
    trackers = "&".join([f"tr={urllib.parse.quote(tracker)}" for tracker in TRACKER_URLS])
    magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(file_name)}&{trackers}"
    return magnet_link

def seed_file(file_path, tracker_list, target_peer_count=5):
    """Function to run the WebTorrent seed command in a separate thread and monitor peers."""
    cmd = f"webtorrent seed '{file_path}' {tracker_list} --keep-seeding"
    logging.info(f"Running seeding command: {cmd}")

    try:
        seed_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        connected_peers = 0
        magnet_url = None

        # Parse the output to extract the magnet URL and number of connected peers
        for line in seed_process.stdout:
            logging.info(f"Seeding output: {line.strip()}")
            if "Magnet:" in line:
                # Store the magnet URL for the file
                magnet_url = line.split("Magnet:")[1].strip()
                seeded_files[file_path] = magnet_url
                logging.info(f"Magnet URL found: {magnet_url}")
            elif "Peers:" in line:
                # Example of WebTorrent output for peers: "Peers: 2/50"
                peer_info = line.split("Peers:")[1].split("/")[0].strip()
                connected_peers = int(peer_info)
                logging.info(f"Connected peers: {connected_peers}")

            # If the target peer count is reached, stop seeding
            if connected_peers >= target_peer_count:
                logging.info(f"Target peer count {target_peer_count} reached. Stopping seeding.")
                break

        stdout, stderr = seed_process.communicate()

        if seed_process.returncode != 0:
            logging.error(f"Error during seeding: {stderr}")
        else:
            logging.info(f"Seeding finished successfully for {file_path}")

        # Log stderr if there's any error
        if stderr:
            logging.error(f"Seeding error output: {stderr}")

    except Exception as e:
        logging.error(f"Seeding process failed: {str(e)}")



def load_seeded_files():
    """Load previously seeded files from the JSON file and resume seeding."""
    logging.debug("Starting load_seeded_files()")
    
    if os.path.exists(SEED_FILE):
        logging.debug(f"Seed file {SEED_FILE} exists. Attempting to load it.")
        try:
            with open(SEED_FILE, 'r') as f:
                seeded = json.load(f)
                logging.info(f"Successfully loaded previously seeded files: {seeded}")
                
                for file_path, magnet_url in seeded.items():
                    logging.debug(f"Preparing to resume seeding for file: {file_path} with magnet: {magnet_url}")
                    tracker_list = " ".join([f"--announce={tracker}" for tracker in TRACKER_URLS])
                    logging.debug(f"Generated tracker list: {tracker_list}")
                    
                    # Start a new thread to seed the file
                    threading.Thread(target=seed_file, args=(file_path, tracker_list)).start()
                    logging.info(f"Started seeding thread for file: {file_path}")
                    
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {SEED_FILE}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading seeded files: {e}")
    else:
        logging.debug(f"Seed file {SEED_FILE} does not exist. Nothing to load.")

def save_seeded_files():
    """Save the current seeded files to a JSON file."""
    logging.debug("Starting save_seeded_files()")
    
    try:
        with open(SEED_FILE, 'w') as f:
            json.dump(seeded_files, f)
            logging.info(f"Successfully saved current seeded files to {SEED_FILE}: {seeded_files}")
    except IOError as e:
        logging.error(f"IOError when saving seeded files to {SEED_FILE}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while saving seeded files: {e}")

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
            # Use 127.0.0.1 for local development instead of localhost
            server_url = f"http://127.0.0.1:5000/static/{filename}"
            logging.info(f"Web seed URL: {server_url}")

            # Build the seed command with trackers
            tracker_list = " ".join([f"--announce={tracker}" for tracker in TRACKER_URLS])

            # Start seeding in a separate thread
            seed_thread = threading.Thread(target=seed_file, args=(file_path, tracker_list))
            seed_thread.start()

            # Poll the shared dictionary until the magnet URL is available
            max_wait_time = 10  # Max wait time in seconds
            wait_time = 0
            while file_path not in seeded_files and wait_time < max_wait_time:
                time.sleep(0.5)  # Sleep for 500ms
                wait_time += 0.5

            if file_path in seeded_files:
                magnet_url = seeded_files[file_path]
                save_seeded_files() 
                logging.info(f"Magnet URL generated: {magnet_url}")
                return jsonify({"magnet_url": magnet_url, "web_seed": server_url}), 200
            else:
                return jsonify({"error": "Failed to generate magnet URL in time"}), 500

        except subprocess.CalledProcessError as e:
            logging.error(f"Error during seeding: {e}")
            return jsonify({"error": "Error creating torrent", "details": str(e)}), 500

    return jsonify({"error": "Invalid file type"}), 400

@app.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve the uploaded image."""
    return send_from_directory(FILE_DIR, filename)

if __name__ == "__main__":
    logging.info("Starting webseed server")
    load_seeded_files()  # Resume seeding on server startup
    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
