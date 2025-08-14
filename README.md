
## TODO

- Support automatic fetching from more chairs.
- Make parsing logic for different chairs configurable.

# Forschungspraxis Internship Scraper

This project provides a script to automatically fetch and track new Forschungspraxis listings from the [EDA website](https://www.ce.cit.tum.de/eda/studentische-arbeiten/offene-arbeiten/), [LKN website](https://www.ce.cit.tum.de/lkn/studentische-arbeiten/) and ...

## Features
- Scrapes the 'Forschungspraxis' section for new internship opportunities.
- Stores and updates a list of published internships in `published_internships.txt`.
- Notifies about new listings found since the last check.
- **Automatically downloads PDF files** for all internship listings.
- **Organizes PDFs with chair-specific naming** (e.g., `EDA-[Title].pdf`, `LKN-[Title].pdf`).
- **Replaces existing PDFs** with newer versions when re-downloading.

## Requirements
- Python 3.11+
- Packages: `requests`, `beautifulsoup4`

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Usage

### Check for New Internships
Run the script to check for new internships:
```bash
python check_internships.py
```
- The script will print new internships (if any) and update `published_internships.txt`.

### Download PDF Files
Download all PDF files for internships listed in `published_internships.txt`:
```bash
python download_pdf.py
```

**Features:**
- **Smart naming**: PDFs are saved with format `{CHAIR}-{Title}.pdf` (e.g., `EDA-Neural Architecture Search for Efficient Vision Transformer.pdf`)
- **Chair identification**: Automatically detects chair from source URL (EDA, LKN)
- **File replacement**: Newer downloads replace existing files instead of creating duplicates


## Files
- `check_internships.py`: Main script for scraping and tracking internships.
- `download_pdf.py`: Script for downloading PDF files of internship listings.
- `published_internships.txt`: Stores the list of internships with format `Title | URL | Source` (auto-updated).
- `downloads/`: Directory containing downloaded PDF files organized by chair.
- `requirements.txt`: Python dependencies.

## Customization
- You can change the target URL or data file by editing the variables at the top of `check_internships.py`.


## Automation: Daily Internship Check (GitHub Actions)

This project includes a GitHub Actions workflow to automatically check for new internships every day and update the repository if new listings are found.

### How it works
- The workflow is defined in `.github/workflows/daily-check.yml`.
- It runs daily at 08:00 UTC (10:00 in Germany during summer) or can be triggered manually.
- Steps performed:
	1. Checks out the repository.
	2. Sets up Python 3.11.
	3. Installs dependencies from `requirements.txt`.
	4. Runs `check_internships.py` to fetch and compare internships.
	5. **If internships file was updated**, automatically runs `download_pdf.py` to download new PDFs.
	6. Commits and pushes both the updated `published_internships.txt` and downloaded PDFs back to the repository.

## License
This project is for educational and personal use. No warranty is provided.
