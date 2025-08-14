import requests
import os
import re
from urllib.parse import urlsplit

def get_filename_from_response(response, url):
    """
    Extract filename from HTTP response headers or URL.
    """
    # Try to get filename from Content-Disposition header
    content_disposition = response.headers.get('Content-Disposition', '')
    if content_disposition:
        # Look for filename parameter in Content-Disposition header
        filename_match = re.search(r'filename[*]?=([^;]+)', content_disposition)
        if filename_match:
            filename = filename_match.group(1).strip('"\'')
            # Remove any path separators for security
            filename = os.path.basename(filename)
            if filename and filename.lower().endswith('.pdf'):
                return filename
    
    # Fallback to URL-based filename
    filename = os.path.basename(urlsplit(url).path)
    if not filename or '.' not in filename:
        filename = 'downloaded.pdf'
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    return filename

def sanitize_filename(filename):
    """
    Remove invalid characters from filename for Windows/Unix compatibility.
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure it's not empty
    if not filename:
        filename = 'downloaded.pdf'
    
    return filename

def extract_chair_from_source(source_url):
    """
    Extract chair name from source URL.
    """
    if 'eda' in source_url.lower():
        return 'EDA'
    elif 'lkn' in source_url.lower():
        return 'LKN'
    else:
        return 'UNKNOWN'

def download_pdf(url, title=None, source_url=None, save_dir="downloads"):
    """
    Download a PDF file from the given URL and save it to the specified directory.
    Uses custom filename based on chair and title when provided.
    If file exists, replace it with the newer version.
    """

    # Check if save_dir exists as a file
    if os.path.exists(save_dir) and not os.path.isdir(save_dir):
        print(f"Error: '{save_dir}' exists and is not a directory. Please remove or rename it.")
        return None
    os.makedirs(save_dir, exist_ok=True)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type:
            print(f"Warning: URL did not return a PDF (Content-Type: {content_type}): {url}")
            return None
        
        # Create custom filename if title and source are provided
        if title and source_url:
            chair = extract_chair_from_source(source_url)
            filename = f"{chair}-{title}.pdf"
            filename = sanitize_filename(filename)
        else:
            # Fallback to original method
            filename = get_filename_from_response(response, url)
            filename = sanitize_filename(filename)
        
        # Set save path - will overwrite if file exists
        save_path = os.path.join(save_dir, filename)
        
        # Check if file already exists and inform user
        if os.path.exists(save_path):
            print(f"File already exists, replacing: {save_path}")
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {save_path}")
        return save_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def download_from_published(file_path="published_internships.txt"):
    """
    Read URLs from the published_internships.txt file and download all PDF links found.
    New format: Title | URL | Source
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    downloaded_count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            parts = line.split("|")
            if len(parts) >= 2:  # Support both old format (2 parts) and new format (3 parts)
                title = parts[0].strip()
                url = parts[1].strip()
                source = parts[2].strip() if len(parts) >= 3 else "Unknown"
                
                print(f"\nDownloading: {title}")
                print(f"Source: {source}")
                print(f"URL: {url}")
                
                result = download_pdf(url, title=title, source_url=source)
                if result:
                    downloaded_count += 1
            else:
                print(f"Warning: Invalid format on line {line_num}: {line}")
    
    print(f"\nDownload completed. Successfully downloaded {downloaded_count} PDFs.")

if __name__ == "__main__":
    print("Downloading all PDFs from published_internships.txt...")
    download_from_published()
