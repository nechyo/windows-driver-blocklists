# check_update.py
import requests
import time
import os
from downloader import get_uuid

def get_update_info(uuid, max_retries=6, retry_delay=10):
    api_url = f'https://api.uupdump.net/get.php?id={uuid}&lang=en-us&edition=professional'
    
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url)
            if response.status_code in (429, 500):  # Rate limit
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            response.raise_for_status()
            data = response.json()
            return data['response']['updateName']
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise e

def check_updates():
    current_uuid = get_uuid()
    update_name = get_update_info(current_uuid)
    
    with open('current_uuid.txt', 'w') as f:
        f.write(current_uuid)
    
    update_needed = True
    if os.path.exists('latest.txt'):
        with open('latest.txt', 'r') as f:
            last_uuid = f.read().strip()
            update_needed = last_uuid != current_uuid
    
    # Use environment files instead of set-output
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"update_name={update_name}\n")
        f.write(f"update_needed={str(update_needed).lower()}\n")
        f.write(f"current_uuid={current_uuid}\n")
    return update_name, update_needed, current_uuid

if __name__ == '__main__':
    check_updates()
