from flask import Blueprint, render_template
from shared import gremlinThreadABI, gremlinThreadAddress, gremlinAdminABI, gremlinAdminAddress, gremlinReplyABI, gremlinReplyAddress, allowed_file, FILE_DIR, seed_file, seeded_files, save_whitelist, save_blacklist, blacklist, whitelist, app, gremlinProfileAddress, gremlinProfileABI, THREADS, StreamSeed
import json, os, threading
from flask import Flask, request, jsonify, send_from_directory
import logging, time
from werkzeug.utils import secure_filename
import subprocess

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
    return render_template(
        'profile.html', 
        eth_address=eth_address, 
        gremlinProfileAddress=gremlinProfileAddress, 
        gremlinProfileABI=gremlinProfileABI, 
        magnet_url=get_magnet_url(eth_address)
    )

import subprocess

@app.route('/live/<eth_address>')
def live_stream(eth_address):
    """Serve the live stream page and continuously monitor and seed HLS segments."""
    hls_dir = os.path.join(FILE_DIR, "hls", eth_address)
    os.makedirs(hls_dir, exist_ok=True)

    # Ensure the directory is writable
    if not os.access(hls_dir, os.W_OK):
        os.chmod(hls_dir, 0o777)

    # RTMP stream input URL and HLS output directory
    rtmp_stream_url = f"rtmp://gremlin.codes:1935/live/{eth_address}"
    hls_output_path = os.path.join(hls_dir, f"{eth_address}.m3u8")

    # RTMP streaming configuration using FFmpeg
    def stream_rtmp_to_hls():
        """Use FFmpeg to capture RTMP stream and convert to HLS."""
        try:
            logging.info(f"Starting FFmpeg to stream RTMP to HLS for {eth_address}...")
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", rtmp_stream_url,
                "-c:v", "copy",
                "-c:a", "copy",
                "-f", "hls",
                "-hls_time", "10",
                "-hls_list_size", "6",
                "-hls_flags", "delete_segments",
                hls_output_path
            ]
            process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for stdout_line in iter(process.stdout.readline, ""):
                logging.info(stdout_line.strip())
            for stderr_line in iter(process.stderr.readline, ""):
                logging.error(stderr_line.strip())
            process.wait()
        except Exception as e:
            logging.error(f"Error streaming RTMP to HLS: {e}")

    # Monitor and seed HLS segments
    def monitor_hls_segments(directory):
        """Monitor the HLS directory for new .ts segments and seed them."""
        already_seeded = set()
        while True:
            try:
                segment_files = sorted([f for f in os.listdir(directory) if f.endswith(".ts")])

                for segment_file in segment_files:
                    if segment_file not in already_seeded:
                        file_path = os.path.join(directory, segment_file)

                        # Start the seeding process using the StreamSeed class
                        stream_seed = StreamSeed(eth_address, file_path, seeded_files)
                        stream_seed.start()  # Start the thread
                        already_seeded.add(segment_file)

                time.sleep(5)  # Check every 5 seconds for new segments
            except Exception as e:
                logging.error(f"Error monitoring HLS segments: {e}")
                break

    ffmpeg_thread = threading.Thread(target=stream_rtmp_to_hls, daemon=True)
    monitor_thread = threading.Thread(target=monitor_hls_segments, args=(hls_dir,), daemon=True)

    # Check if the stream is already running for this RTMP URL
    if (rtmp_stream_url not in [x[0] for x in THREADS]):
        ffmpeg_thread.start()  # Start FFmpeg RTMP to HLS conversion in a separate thread
        monitor_thread.start()  # Start monitoring and seeding in a separate thread
        THREADS.append(tuple((rtmp_stream_url, ffmpeg_thread, monitor_thread)))
    else:
        logging.info(f"Already streaming {eth_address}")

    return render_template('profile.html', eth_address=eth_address)


@app.route('/magnet_url/<eth_address>')
def get_magnet_url(eth_address):
    """Get the latest magnet URL for the given user's stream."""
    if (eth_address in seeded_files.keys()):
        latest_magnet_url = list(seeded_files[eth_address])[-1]
        return jsonify({"magnet_url": latest_magnet_url}), 200
    else:
        return jsonify({"error": "No segments found"}), 404