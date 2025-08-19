import requests
import os
import re
import time
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

def download_pdf(url, title=None, source_url=None, save_dir="downloads", max_retries=3, timeout=30):
    """
    Download a PDF file from the given URL and save it to the specified directory.
    Uses custom filename based on chair and title when provided.
    If file exists, replace it with the newer version.
    Includes retry mechanism and timeout handling for better reliability.
    """

    # Check if save_dir exists as a file
    if os.path.exists(save_dir) and not os.path.isdir(save_dir):
        print(f"Error: '{save_dir}' exists and is not a directory. Please remove or rename it.")
        return None
    os.makedirs(save_dir, exist_ok=True)

    # Setup session with headers and timeout
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            response = session.get(url, stream=True, timeout=timeout)
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
            
        except requests.exceptions.Timeout:
            print(f"Timeout error on attempt {attempt + 1}. Retrying in {2 ** attempt} seconds...")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    print(f"Failed to download after {max_retries} attempts: {url}")
    return None

def download_from_published(file_path="published_internships.txt", skip_on_network_error=False):
    """
    Read URLs from the published_internships.txt file and download all PDF links found.
    New format: Title | URL | Source
    
    Args:
        file_path: Path to the internships file
        skip_on_network_error: If True, skip downloads on network errors (useful for CI environments)
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    downloaded_count = 0
    failed_count = 0
    
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
                
                # Quick network test for CI environments
                if skip_on_network_error:
                    try:
                        import socket
                        socket.setdefaulttimeout(10)
                        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('tumanager.ei.tum.de', 443))
                    except Exception as e:
                        print(f"Network connectivity test failed: {e}")
                        print("Skipping downloads due to network issues in CI environment")
                        return
                
                result = download_pdf(url, title=title, source_url=source)
                if result:
                    downloaded_count += 1
                else:
                    failed_count += 1
            else:
                print(f"Warning: Invalid format on line {line_num}: {line}")
    
    print(f"\nDownload completed. Successfully downloaded {downloaded_count} PDFs.")
    if failed_count > 0:
        print(f"Failed to download {failed_count} PDFs due to network or server issues.")
    
    # Exit with success even if some downloads failed (important for CI)
    return downloaded_count

if __name__ == "__main__":
    import sys
    
    # Check if we're running in a CI environment or with skip flag
    skip_on_network_error = '--skip-on-network-error' in sys.argv or os.environ.get('CI') == 'true'
    
    if skip_on_network_error:
        print("Running in CI mode with network error handling...")
    
    print("Downloading all PDFs from published_internships.txt...")
    download_from_published(skip_on_network_error=skip_on_network_error)
