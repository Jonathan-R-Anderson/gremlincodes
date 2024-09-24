from flask import Blueprint, render_template
from shared import gremlinThreadABI, gremlinThreadAddress, gremlinAdminABI, gremlinAdminAddress, gremlinReplyABI, gremlinReplyAddress, allowed_file, FILE_DIR, seed_file, seeded_files, save_whitelist, save_blacklist, blacklist, whitelist, app, gremlinProfileAddress, gremlinProfileABI, seed_stream
import json, os, threading
from flask import Flask, request, jsonify, send_from_directory
import logging, time
from werkzeug.utils import secure_filename

blueprint = Blueprint('blueprint', __name__)
logging.basicConfig(level=logging.DEBUG)

@blueprint.route('/')
def index():
    return render_template('index.html', 
                           gremlinThreadABI=json.dumps(gremlinThreadABI, ensure_ascii=False),  # Avoid ASCII escaping
                           gremlinThreadAddress=gremlinThreadAddress,
                           gremlinAdminABI=json.dumps(gremlinAdminABI, ensure_ascii=False),  # Avoid ASCII escaping
                           gremlinAdminAddress=gremlinAdminAddress,
                           gremlinReplyABI=json.dumps(gremlinReplyABI, ensure_ascii=False),
                           gremlinReplyAddress=gremlinReplyAddress)




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
            logging.info(f"File successfully saved to {file_path}")

            # Start seeding in a separate thread
            seed_thread = threading.Thread(target=seed_file, args=(file_path,))
            seed_thread.start()

            # Poll the seeded_files dictionary until the magnet URL is available
            max_wait_time = 60  # Max wait time in seconds
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
        logging.error(f"Invalid file type: {file.filename}")
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

@app.route('/users/<eth_address>')
def user_profile(eth_address):
    """Serve the user's profile page and provide the RTMP stream URL."""
    # Assuming the user is the profile owner; generate an RTMP URL
    rtmp_url = f"rtmp://your-server-address/live/{eth_address}"
    return render_template(
        'profile.html', 
        eth_address=eth_address, 
        gremlinProfileAddress=gremlinProfileAddress, 
        gremlinProfileABI=gremlinProfileABI, 
        rtmp_url=rtmp_url
    )


@app.route('/stream/upload', methods=['POST'])
def upload_stream_segment():
    """Handle the file upload from OBS and seed the stream segment using WebTorrent."""
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('/app/static/', filename)
        file.save(file_path)

        # Seed the file using WebTorrent and return the magnet URL
        magnet_url = seed_stream(file_path)

        if magnet_url:
            return jsonify({'magnet_url': magnet_url}), 200
        else:
            return jsonify({'error': 'Failed to seed the file'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@app.route('/live/<stream_id>')
def live_stream(stream_id):
    """Serve the live stream page and start WebTorrent seeding."""
    hls_path = f"/var/www/hls/{stream_id}"  # Path to HLS segments
    magnet_url = seed_stream(hls_path)  # Start seeding the stream

    return render_template('live.html', magnet_url=magnet_url)
