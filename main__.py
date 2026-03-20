import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin

def get_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return [tag['href'] for tag in soup.find_all('a', href=True)]

from urllib.parse import unquote, urljoin

def process_links(links, base_url):
    processed_links = {}
    forbidden = ["rev","beta","taiwan", "germany", "europe", "united kingdom", "spain", "asia", "italy","russia","france","netherlands","portugal"]
    
    for link in links:
        filename = unquote(link.split('/')[-1])
        fn_lower = filename.lower()
        
        if filename.endswith(".zip"):
            # Check if filename contains any forbidden words
            has_forbidden = any(word in fn_lower for word in forbidden)
            # Check if filename contains USA
            has_usa = "usa" in fn_lower

            # Logic: If it has a forbidden word but NO "USA", skip it.
            if has_forbidden and not has_usa:
                continue

            clean_name = filename.replace(".zip", "")
            full_url = urljoin(base_url, link)
            processed_links[clean_name] = (filename, full_url)
                
    return processed_links

def download_file(filename, url, save_dir, headers):
    file_path = os.path.join(save_dir, filename)
    
    # Skip if the file is already safely on your hard drive
    if os.path.exists(file_path):
        print(f"Already exists, skipping: {filename}")
        return

    print(f"Downloading: {filename}...")
    # stream=True keeps the script from loading the whole file into RAM at once
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def main():
    base_url = "https://myWebsite"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    save_dir = "downloads"
    
    os.makedirs(save_dir, exist_ok=True)
    
    print("Fetching file list...")
    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        links = get_links(response.text)
        processed_links = process_links(links, base_url)
        
        print(f"Found {len(processed_links)} files. Starting download...")
        
        for clean_name, (filename, full_url) in processed_links.items():
            download_file(filename, full_url, save_dir, headers)
            
        print("\nAll downloads complete!")
    else:
        print("Failed to retrieve webpage. Status code:", response.status_code)

if __name__ == "__main__":
    main()