import requests
from bs4 import BeautifulSoup
import re
import os

# Target website URLs
URLS = [
    "https://www.ce.cit.tum.de/eda/studentische-arbeiten/offene-arbeiten/",
    "https://www.ce.cit.tum.de/lkn/studentische-arbeiten/"
]
# File to store published internship information
DATA_FILE = "published_internships.txt"

def get_research_internships_eda(url):
    """
    Fetch and parse 'Forschungspraxis' internship listings from the EDA website.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to access {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    internships = []

    # Locate the "Forschungspraxis" heading
    praxis_heading = soup.find("h3", string=re.compile(r'Forschungspraxis'))
    if not praxis_heading:
        print(f"Warning: Could not find the 'Forschungspraxis' section on {url}")
        return []

    # Iterate through siblings after the heading
    for sibling in praxis_heading.find_next_siblings():
        if sibling.name == 'h3':  # Stop at the next H3
            break

        if sibling.name == 'div' and 'accordion' in sibling.get('class', []):
            title_button = sibling.find('button')
            details_div = sibling.find('div', class_='collapse')

            if title_button and details_div:
                title = title_button.get_text(strip=True).replace('+', '').replace('-', '').strip()
                link_tag = details_div.find('a', href=True)

                if link_tag:
                    link = link_tag['href']
                    internships.append({"title": title, "link": link, "source": url})

    return internships

def get_research_internships_lkn(url):
    """
    Fetch and parse 'FP' (Forschungspraxis) internship listings from the LKN website.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to access {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    internships = []

    # Find all accordion elements
    accordion_divs = soup.find_all('div', class_='accordion')
    
    for accordion in accordion_divs:
        # Look for the button that contains the title
        title_button = accordion.find('button')
        if not title_button:
            continue
            
        title_text = title_button.get_text(strip=True)
        
        # Check if this is an FP (Forschungspraxis) listing
        if re.search(r'<abbr[^>]*title="Forschungspraxis \(Research Internship\)"[^>]*>FP</abbr>', str(title_button)) or \
           'FP:' in title_text:
            
            # Extract the actual title (after the abbreviations)
            # Remove the abbreviation parts and clean up
            title_clean = re.sub(r'^.*?:', '', title_text).strip()
            title_clean = re.sub(r'[+\-\s]+$', '', title_clean).strip()
            
            # Find the collapse div with the download link
            collapse_div = accordion.find('div', class_='collapse')
            if collapse_div:
                link_tag = collapse_div.find('a', href=True)
                if link_tag and 'pdfdownload' in link_tag.get('href', ''):
                    link = link_tag['href']
                    # Make sure the link is absolute
                    if link.startswith('https://'):
                        full_link = link
                    else:
                        full_link = url.rstrip('/') + '/' + link.lstrip('/')
                    
                    internships.append({"title": title_clean, "link": full_link, "source": url})

    return internships

def get_all_research_internships():
    """
    Fetch internships from all configured websites.
    """
    all_internships = []
    
    for url in URLS:
        if 'eda' in url:
            internships = get_research_internships_eda(url)
        elif 'lkn' in url:
            internships = get_research_internships_lkn(url)
        else:
            print(f"Unknown website format: {url}")
            continue
            
        all_internships.extend(internships)
        print(f"Found {len(internships)} FP internships from {url}")
    
    return all_internships

def check_for_new_internships():
    """
    Check for new internship listings from all configured websites and update the file with title + link.
    """
    print("Checking for new 'Forschungspraxis' internships from multiple sources...")
    for url in URLS:
        print(f"  - {url}")
    
    current_internships = get_all_research_internships()

    if not current_internships:
        print("No 'Forschungspraxis' internships found or failed to scrape from any source.")
        return

    print(f"\nTotal internships found: {len(current_internships)}")

    # Load previously stored internships
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            seen_entries = set(line.strip() for line in f)
    except FileNotFoundError:
        seen_entries = set()

    new_listings = []
    all_entries = set()

    for internship in current_internships:
        entry_str = f"{internship['title']} | {internship['link']} | {internship['source']}"
        all_entries.add(entry_str)

        if entry_str not in seen_entries:
            new_listings.append(internship)

    if new_listings:
        print("\n🎉 Found new Forschungspraxis internships!")
        for listing in new_listings:
            print(f"\n  **Title:** {listing['title']}")
            print(f"  **Link:** {listing['link']}")
            print(f"  **Source:** {listing['source']}")

    # Always write the full updated list
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for entry in sorted(all_entries):  # keep sorted for consistency
            f.write(entry + "\n")

    print(f"\nUpdated '{DATA_FILE}' with the latest list.")

if __name__ == "__main__":
    check_for_new_internships()
