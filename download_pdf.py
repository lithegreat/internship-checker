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

def download_pdf(url, save_dir="downloads"):
    """
    Download a PDF file from the given URL and save it to the specified directory.
    Uses the actual PDF filename from server response when available.
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
        
        # Get the actual filename from response or URL
        filename = get_filename_from_response(response, url)
        filename = sanitize_filename(filename)
        
        # Handle duplicate filenames
        save_path = os.path.join(save_dir, filename)
        counter = 1
        original_filename = filename
        while os.path.exists(save_path):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            save_path = os.path.join(save_dir, filename)
            counter += 1
        
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
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|", 1)
            if len(parts) == 2:
                url = parts[1].strip()
                download_pdf(url)

if __name__ == "__main__":
    print("Downloading all PDFs from published_internships.txt...")
    download_from_published()
