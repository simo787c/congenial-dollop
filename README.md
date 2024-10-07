# Required libraries

selenium                     4.25.0

beautifulsoup4               4.12.3

requests                     2.28.2


# Setup
1. create env and install required libraries


# Usage
1. First, run scrape_links.py to save all found links within the list to document_links.json
2. Run scrape_and_convert.py to scrape each links specified xml contents, Source, Meta and document text, to scraped_data.json
3. Data is contained in scraped_data.json for further processing
