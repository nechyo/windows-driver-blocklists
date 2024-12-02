import requests
import hashlib
import os
import time
from tqdm import tqdm
from requests.exceptions import RequestException
import subprocess

def list_builds(search_query=None, sort_by_date=True):
    try:
        api_url = "https://api.uupdump.net/listid.php"
        params = {
            "search": search_query if search_query else "",
            "sortByDate": 1 if sort_by_date else 0
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        builds = data.get("response", {}).get("builds", [])
        
        if not builds:
            print("No builds found.")
            return []
        
        return builds
            
    except RequestException as e:
        raise Exception(f"Error listing builds: {e}")

def get_download_url(uuid, max_retries=6, initial_delay=10):
    api_url = f"https://api.uupdump.net/get.php?id={uuid}&lang=en-us&edition=professional"
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            file_info = data['response']['files']['MetadataESD_professional_en-us.esd']
            return file_info['url'], file_info['sha256']
        except RequestException as e:
            if response.status_code == 429 and attempt < max_retries - 1:
                print(f"Rate limited. Waiting {delay} seconds...")
                time.sleep(delay)
                delay *= 2
                continue
            raise Exception(f"Error getting download URL: {e}")
    raise Exception("Max retries exceeded")

def download_esd(url, output_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    pbar.update(size)
    except requests.RequestException as e:
        raise Exception(f"Error downloading ESD: {e}")

def verify_sha256(file_path, expected_hash):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash

def process_all_builds():
    try:
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        assets_dir = "assets"
        os.makedirs(assets_dir, exist_ok=True)
        
        print("Fetching list of builds...")
        builds = list_builds()
        if not builds:
            print("No builds available. Exiting.")
            return
        
        for build in builds:
            uuid = build.get("uuid")
            title = build.get("title", "Unknown Title")
            safe_title = title.replace(' ', '_').replace(':', '-').replace('/', '_')
            file_name = f"{safe_title}_{uuid}.esd"
            output_path = os.path.join(assets_dir, file_name)
            
            print(f"Processing build: {title} (UUID: {uuid})")
            
            try:
                download_url, expected_hash = get_download_url(uuid)
                download_esd(download_url, output_path)
                
                print("Verifying file integrity...")
                if not verify_sha256(output_path, expected_hash):
                    raise Exception("SHA256 verification failed - file may be corrupted")
                print(f"File integrity verified for {title}!")
            except Exception as e:
                print(f"Error processing build {title}: {e}")
                if os.path.exists(output_path):
                    os.remove(output_path)
        
        print("All builds processed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_all_builds()
