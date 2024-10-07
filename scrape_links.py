from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

# Initialize the WebDriver
driver = webdriver.Chrome()
driver.get('https://www.retsinformation.dk/documents?dt=20&dt=80&h=false&ps=100')

# Optional: wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-result-list')))

# List to store all document links
all_document_links = []

# Function to extract links from the current page
def extract_links(soup):
    search_results = soup.find('div', class_='search-result-list')
    document_entries = search_results.find_all('div', class_='document-entry')

    page_links = []  # Store links per page for easier verification
    for entry in document_entries:
        document_link = entry.get('about')
        if document_link:
            full_document_url = f"https://www.retsinformation.dk{document_link}/xml"
            page_links.append(full_document_url)
            print(f"Document URL: {full_document_url}")

    return page_links

# Function to scrape a page with retries
def scrape_page(page_number, retries=3):
    for attempt in range(retries):
        print(f"Scraping page {page_number}... Attempt {attempt + 1}/{retries}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        page_links = extract_links(soup)

        if len(page_links) > 0:  # Proceed if links are found
            return page_links
        else:
            print(f"Warning: No links found on page {page_number} (Attempt {attempt + 1}). Retrying...")
            time.sleep(3)  # Wait before retrying

    # If retries failed, return an empty list and continue
    print(f"Failed to scrape page {page_number} after {retries} attempts. Skipping to next page.")
    return []

# Loop through pages and extract links
page_number = 1  # Track the page number for debugging
while True:
    page_links = scrape_page(page_number)
    
    # Even if no links were found, just continue to the next page
    all_document_links.extend(page_links)

    try:
        # Wait for the "Next" button
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Næste'))
        )

        # Check if the "Next" button is disabled
        if next_button.get_attribute('disabled'):
            print(f"No next page available. Reached the last page (Page {page_number}).")
            break

        # Click the "Next" button to go to the next page
        next_button.click()

        # Wait for the new page to load
        time.sleep(5)

        # Increment page number for tracking
        page_number += 1

    except Exception as e:
        print(f"An error occurred while trying to navigate to the next page (Page {page_number}): {e}")
        break

# Close the driver after finishing
driver.quit()

# Now `all_document_links` contains document URLs from all pages
print(f"Total Document Links Found: {len(all_document_links)}")

# Save the document links to a JSON file
with open('document_links.json', 'w', encoding='utf-8') as f:
    json.dump(all_document_links, f, ensure_ascii=False, indent=4)
