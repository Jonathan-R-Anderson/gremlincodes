import os
import logging
import threading
import time
import json
import urllib
from shared import app, FILE_DIR, TORRENT_DIR, TRACKER_PORT, auto_seed_static_files
from blueprints.routes import blueprint
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

CORS(app)

app.register_blueprint(blueprint)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Setup directories
os.makedirs(FILE_DIR, exist_ok=True)
os.makedirs(TORRENT_DIR, exist_ok=True)



if __name__ == "__main__":
    logging.info("Starting webseed server")
    
    # Automatically seed files in the static directory
    auto_seed_static_files()

    app.run(host="0.0.0.0", port=TRACKER_PORT, debug=True)
