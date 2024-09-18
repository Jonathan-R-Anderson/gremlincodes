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
from blueprints.routes import blueprint


app.register_blueprint(blueprint)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Setup directories
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 5000
SEED_FILE = 'seeded_files.json'
BLACKLIST_FILE = 'blacklist.json'
WHITELIST_FILE = 'whitelist.json'
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

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return []  # Return empty list if file does not exist
    with open(BLACKLIST_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # Return empty list if file is corrupt or empty

# Load whitelist from file, if it exists, otherwise return an empty list
def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return []  # Return empty list if file does not exist
    with open(WHITELIST_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # Retur

def save_blacklist(data):
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(data, f)


def save_whitelist(data):
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(data, f)


# Initialize blacklist and whitelist
blacklist = load_blacklist()
whitelist = load_whitelist()

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def seed_file(file_path):
    """Function to seed the file using the WebTorrent command and stop seeding after enough peers."""
    try:
        # Check if the file is already being seeded
        if file_path in seeded_files:
            #logging.info(f"{file_path} is already being seeded.")
            return seeded_files[file_path]  # Return existing magnet URL if it's already seeded

        # Prepare tracker list for WebTorrent seed command
        tracker_list = " ".join([f"--announce={tracker}" for tracker in TRACKER_URLS])
        
        # WebTorrent seed command with trackers and keep-seeding
        cmd = f"webtorrent seed '{file_path}' {tracker_list} --keep-seeding"
        #logging.info(f"Running seeding command: {cmd}")

        # Run the command in a subprocess
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        magnet_url = None
        peer_count = 0

        # Read output to extract magnet link and check peers
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break

            if output:
                #logging.info(f"WebTorrent output: {output.strip()}")
                if "Magnet URI:" in output:
                    magnet_url = output.split("Magnet URI:")[1].strip()
                    seeded_files[file_path] = magnet_url
                    #logging.info(f"Magnet URL found: {magnet_url}")

                if peer_count >= 5:
                    #logging.info(f"Stopping seeding for {file_path} after reaching {peer_count} peers")
                    process.terminate()
                    break

        process.communicate()
        return magnet_url

    except Exception as e:
        logging.error(f"Error while seeding file: {str(e)}")
        return None


def auto_seed_static_files():
    """Automatically seed all allowed files in the static directory."""
    for filename in os.listdir(FILE_DIR):
        file_path = os.path.join(FILE_DIR, filename)
        if os.path.isfile(file_path) and allowed_file(filename):
            #logging.info(f"Automatically seeding {file_path}")
            seed_thread = threading.Thread(target=seed_file, args=(file_path,))
            seed_thread.start()


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle the image upload, start torrent seeding in a separate thread, and return the magnet link."""
    logging.info('Upload route accessed')  # Log route access
    
    if 'file' not in request.files:
        logging.error('No file part in the request')  # Log missing file part
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        logging.error('No file selected')  # Log empty filename
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(os.path.abspath(FILE_DIR), filename)
        
        logging.info(f"Attempting to save file: {filename} at {file_path}")  # Log file details

        try:
            file.save(file_path)  # Save the file
            logging.info(f"File successfully saved to {file_path}")  # Confirm file saved

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
                logging.error('Failed to generate magnet URL in time')
                return jsonify({"error": "Failed to generate magnet URL in time"}), 500

        except Exception as e:
            logging.error(f"Error during file saving or torrent creation: {e}")
            return jsonify({"error": "Error creating torrent", "details": str(e)}), 500

    else:
        logging.error(f"Invalid file type: {file.filename}")  # Log invalid file type
        return jsonify({"error": "Invalid file type"}), 400


@app.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve the uploaded image."""
    return send_from_directory(FILE_DIR, filename)


# Route to add to blacklist
@app.route('/admin/blacklist/<item_type>', methods=['POST'])
def add_to_blacklist(item_type):
    data = request.json
    if item_type in ['tag', 'magnet', 'user']:
        blacklist_key = f"{item_type}s"  # "tags", "magnet_urls", or "users"
        item_value = data[item_type]
        if item_value not in blacklist[blacklist_key]:
            blacklist[blacklist_key].append(item_value)
            save_blacklist(blacklist)
            return jsonify({"message": f"{item_type.capitalize()} '{item_value}' added to blacklist"}), 200
        return jsonify({"error": f"{item_type.capitalize()} already blacklisted"}), 400
    return jsonify({"error": "Invalid blacklist type"}), 400

# Route to add to whitelist
@app.route('/admin/whitelist/<item_type>', methods=['POST'])
def add_to_whitelist(item_type):
    data = request.json
    if item_type in ['tag', 'magnet', 'user']:
        whitelist_key = f"{item_type}s"  # "tags", "magnet_urls", or "users"
        item_value = data[item_type]
        if item_value not in whitelist[whitelist_key]:
            whitelist[whitelist_key].append(item_value)
            save_whitelist(whitelist)
            return jsonify({"message": f"{item_type.capitalize()} '{item_value}' added to whitelist"}), 200
        return jsonify({"error": f"{item_type.capitalize()} already whitelisted"}), 400
    return jsonify({"error": "Invalid whitelist type"}), 400

# Route to get current blacklist
@app.route('/admin/blacklist', methods=['GET'])
def get_blacklist():
    return jsonify(blacklist)

# Route to get current whitelist
@app.route('/admin/whitelist', methods=['GET'])
def get_whitelist():
    return jsonify(whitelist)


if __name__ == "__main__":
    logging.info("Starting webseed server")
    
    # Automatically seed files in the static directory
    auto_seed_static_files()

    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
