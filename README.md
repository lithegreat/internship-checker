
## TODO

- Support automatic fetching from more chairs.
- Make parsing logic for different chairs configurable.

# Forschungspraxis Internship Scraper

This project provides a script to automatically fetch and track new 'Forschungspraxis' internship listings from the [TUM EDA website](https://www.ce.cit.tum.de/eda/studentische-arbeiten/offene-arbeiten/).

## Features
- Scrapes the 'Forschungspraxis' section for new internship opportunities.
- Stores and updates a list of published internships in `published_internships.txt`.
- Notifies about new listings found since the last check.

## Requirements
- Python 3.11+
- Packages: `requests`, `beautifulsoup4`

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Usage
Run the script to check for new internships:
```bash
python check_internships.py
```

- The script will print new internships (if any) and update `published_internships.txt`.

## Files
- `check_internships.py`: Main script for scraping and tracking internships.
- `published_internships.txt`: Stores the list of internships (auto-updated).
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
	5. If there are new internships, commits and pushes the updated `published_internships.txt` back to the repository.

## License
This project is for educational and personal use. No warranty is provided.
