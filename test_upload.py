import requests
import subprocess
import time

# URL of your Flask server
UPLOAD_URL = "http://localhost:5000/upload"  # Adjust port if needed
LOCAL_SERVER_URL = "http://localhost:5000/static/gremlin.png"  # Web seed URL

# Path to the test image you want to upload
IMAGE_PATH = "gremlin.png"  # Change this to your test image path

def upload_image(image_path):
    """Uploads an image to the Flask server and returns the server's response."""
    try:
        # Open the image file in binary mode
        with open(image_path, 'rb') as image_file:
            # Prepare the file payload for the request
            files = {'file': image_file}
            # Send the POST request to upload the image
            response = requests.post(UPLOAD_URL, files=files)
            
            # Check if the response is successful
            if response.status_code == 200:
                server_response = response.json()
                print(f"Upload successful! Server response: {server_response}")
                return server_response
            else:
                print(f"Upload failed! Status code: {response.status_code}, Response: {response.json()}")
    
    except FileNotFoundError:
        print(f"File '{image_path}' not found. Please provide a valid image file.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return None

def download_torrent_using_trackers(magnet_url):
    """Downloads the torrent using WebTorrent CLI and the provided magnet link."""
    try:
        print("Starting download via trackers...")
        cmd = f"webtorrent download '{magnet_url}' --out ./downloaded_from_trackers"
        subprocess.run(cmd, shell=True, check=True)
        print("Download from trackers completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading from trackers: {e}")

def download_via_local_web_seed(web_seed_url):
    """Downloads the file directly using the local web seed (HTTP)."""
    try:
        print("Starting download via local web seed...")
        response = requests.get(web_seed_url, stream=True)
        if response.status_code == 200:
            with open('downloaded_from_web_seed.png', 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=1024):
                    out_file.write(chunk)
            print("Download from web seed completed successfully!")
        else:
            print(f"Failed to download from web seed. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading from web seed: {e}")

if __name__ == "__main__":
    # Step 1: Upload the image and get the magnet URL and web seed URL
    server_response = upload_image(IMAGE_PATH)
    
    if server_response:
        magnet_url = server_response.get("magnet_url")
        web_seed_url = server_response.get("web_seed")

        if magnet_url:
            # Step 2: Download using the torrent trackers (using magnet URL)
            download_torrent_using_trackers(magnet_url)
            
            # Wait briefly before starting the next download
            time.sleep(5)

            # Step 3: Download using the local web seed (HTTP)
            download_via_local_web_seed(web_seed_url)
        else:
            print("No magnet URL provided in the server response.")
