from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load document links from JSON file
with open('document_links.json', 'r', encoding='utf-8') as file:
    document_links = json.load(file)

# Initialize the WebDriver
driver = webdriver.Chrome()

# Initialize a list to store scraped data for this session
all_scraped_data = []

# Function to extract data from XML
def extract_data_from_xml(xml_soup, source_link):
    extracted_data = {}
    extracted_data['Source'] = source_link

    # Extract all child elements from the <Meta> section
    meta_data = xml_soup.find('Meta')
    if meta_data:
        for child in meta_data.find_all():
            extracted_data[child.name] = child.get_text(strip=True)

    # Extract and combine the text content from <DokumentIndhold>
    dokument_indhold = xml_soup.find('DokumentIndhold')
    full_text_content = []

    if dokument_indhold:
        for paragraph in dokument_indhold.find_all(['AendringCentreretParagraf', 'IkraftCentreretParagraf']):
            for exitus in paragraph.find_all('Exitus'):
                for linea in exitus.find_all('Linea'):
                    line_texts = [char.get_text(strip=True) for char in linea.find_all('Char')]
                    full_text_content.append(' '.join(line_texts))

    combined_text = '\n\n'.join(full_text_content)
    extracted_data['DokumentIndhold'] = combined_text

    return extracted_data

# Function to scrape a document with retries
def scrape_document(link, retries=3):
    for attempt in range(retries):
        try:
            print(f"Scraping {link}... Attempt {attempt + 1}/{retries}")
            # Navigate to the XML document URL
            driver.get(link)

            # time.sleep(5)  # Wait for the XML content to load

            # Wait for the XML content to load
            # Wait for a specific XML tag to be present, like <Meta> or <DokumentIndhold>
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//Meta"))
            )

            # Get the page source (which should now be XML content)
            xml_page_source = driver.page_source

            # Parse the XML content with BeautifulSoup
            xml_soup = BeautifulSoup(xml_page_source, 'xml')

            # Extract data and include the source link
            document_data = extract_data_from_xml(xml_soup, link)

            print(f"Successfully scraped data from: {link}")
            return document_data  # Return the data if scraping succeeds

        except Exception as e:
            print(f"Error occurred while processing {link} on attempt {attempt + 1}: {e}")
            time.sleep(3)  # Wait before retrying

    # If all attempts fail, return None to indicate skipping
    print(f"Failed to scrape {link} after {retries} attempts. Skipping...")
    return None

# Loop through each document link
for link in document_links:
    document_data = scrape_document(link)

    if document_data:  # Only append if scraping was successful
        all_scraped_data.append(document_data)

        # Save the updated data to JSON file after each successful scrape
        with open('scraped_data.json', 'w', encoding='utf-8') as outfile:
            json.dump(all_scraped_data, outfile, indent=4, ensure_ascii=False)

    print(f"Total documents scraped so far: {len(all_scraped_data)}")

# Close the driver when done
driver.quit()

# Print the total number of documents scraped during this execution
print(f"Scraping completed. Total documents scraped this run: {len(all_scraped_data)}")
