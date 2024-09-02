from flask import Flask, send_from_directory, request, Response
import os
import logging
import time

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Setup directories and Flask app
FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 5000

os.makedirs(FILE_DIR, exist_ok=True)
os.makedirs(TORRENT_DIR, exist_ok=True)

# Dictionary to keep track of active torrents and peers
active_peers = {}
webseed_active = True  # Indicates if the webseed is still active

# Define the path to the image file
IMAGE_FILE = 'example.jpg'  # Replace with your image file name
IMAGE_PATH = os.path.join(FILE_DIR, IMAGE_FILE)

# Torrent trackers to be used for distribution
TRACKER_URLS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "http://tracker.opentrackr.org:1337/announce",
    # Add more trackers from the list you provided...
]

def add_peer(info_hash, peer_id):
    """ Add a peer to the active_peers dictionary. """
    if info_hash in active_peers:
        if peer_id not in active_peers[info_hash]:
            active_peers[info_hash].append(peer_id)
    else:
        active_peers[info_hash] = [peer_id]

@app.route('/announce', methods=['GET'])
def announce():
    """ This route no longer acts as a tracker, but will monitor peers. """
    global webseed_active
    
    # Extract info_hash and peer_id from request
    info_hash = request.args.get("info_hash")
    peer_id = request.args.get("peer_id")
    
    if not info_hash or not peer_id:
        return Response(status=400)
    
    # Add peer to the active list
    add_peer(info_hash, peer_id)
    
    # If more than one peer (excluding the webseed itself) exists, deactivate the webseed
    if len(active_peers.get(info_hash, [])) > 1 and webseed_active:
        logging.debug(f"More than one peer detected for {info_hash}. Disabling webseed.")
        webseed_active = False
    
    return Response(status=200)

@app.route('/<path:filename>', methods=['GET'])
def serve_file(filename):
    """ Serve the image file as a webseed until there are sufficient peers. """
    global webseed_active

    if webseed_active and filename == IMAGE_FILE:
        logging.debug(f"Serving {filename} as webseed.")
        return send_from_directory(FILE_DIR, filename)
    else:
        return Response(status=404)

if __name__ == "__main__":
    logging.debug("Starting webseed server")
    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
