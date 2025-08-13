import requests
from bs4 import BeautifulSoup
import re
import os

# Target website URL
URL = "https://www.ce.cit.tum.de/eda/studentische-arbeiten/offene-arbeiten/"
# File to store published internship information
DATA_FILE = "published_internships.txt"

def get_research_internships():
    """
    Fetch and parse 'Forschungspraxis' internship listings from the website.
    """
    try:
        response = requests.get(URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to access the website: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    internships = []

    # Locate the "Forschungspraxis" heading
    praxis_heading = soup.find("h3", string=re.compile(r'Forschungspraxis'))
    if not praxis_heading:
        print("Error: Could not find the 'Forschungspraxis' section on the page.")
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
                    internships.append({"title": title, "link": link})

    return internships

def check_for_new_internships():
    """
    Check for new internship listings and update the file with title + link.
    """
    print(f"Checking for new 'Forschungspraxis' internships... ({URL})")
    current_internships = get_research_internships()

    if not current_internships:
        print("No 'Forschungspraxis' internships found or failed to scrape.")
        return

    # Load previously stored internships
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            seen_entries = set(line.strip() for line in f)
    except FileNotFoundError:
        seen_entries = set()

    new_listings = []
    all_entries = set()

    for internship in current_internships:
        entry_str = f"{internship['title']} | {internship['link']}"
        all_entries.add(entry_str)

        if entry_str not in seen_entries:
            new_listings.append(internship)

    if new_listings:
        print("\n🎉 Found new Forschungspraxis internships!")
        for listing in new_listings:
            print(f"\n  **Title:** {listing['title']}")
            print(f"  **Link:** {listing['link']}")

    # Always write the full updated list
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for entry in sorted(all_entries):  # keep sorted for consistency
            f.write(entry + "\n")

    print(f"\nUpdated '{DATA_FILE}' with the latest list.")

if __name__ == "__main__":
    check_for_new_internships()
