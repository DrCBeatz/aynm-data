

import logging
import re
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def extract_email_from_text(text):
    """
    Searches for a basic pattern of an email address within text using regex.
    This is a fallback if we don't find 'mailto:' links.
    """
    # This pattern looks for sequences of chars@chars.domain
    pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def main():
    csv_file = 'kingston_catholic_schools.csv'
    logging.info(f"Loading CSV file: {csv_file}")
    
    df = pd.read_csv(csv_file)
    if 'Email' not in df.columns:
        df['Email'] = ''

    driver = webdriver.Chrome()  # Ensure 'chromedriver' is on your PATH.

    try:
        for index, row in df.iterrows():
            school_name = str(row.get('School Name', ''))
            website_url = str(row.get('Website', ''))
            logging.info(f"Processing row {index} - School: {school_name}, URL: {website_url}")

            if website_url.startswith('http'):
                try:
                    # Navigate to the website
                    driver.get(website_url)
                    
                    # Wait a bit if the site is known to load slowly
                    time.sleep(3)

                    # Option 1: Search for a mailto: anchor via Selenium
                    mailto_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]')

                    email_found = None
                    if mailto_elements:
                        # Just grab the first 'mailto:' link
                        href_value = mailto_elements[0].get_attribute('href')
                        email_found = href_value.replace('mailto:', '').strip()
                        logging.info(f"Found mailto link for '{school_name}': {email_found}")
                    else:
                        # Option 2: If no mailto link, fallback to page source + regex
                        page_source = driver.page_source
                        email_found = extract_email_from_text(page_source)
                        if email_found:
                            logging.info(f"Found regex-based email for '{school_name}': {email_found}")
                        else:
                            logging.info(f"No email found on '{website_url}' for '{school_name}' via mailto or regex.")
                    
                    # Update DataFrame
                    df.at[index, 'Email'] = email_found if email_found else ''
                
                except Exception as e:
                    logging.error(f"Error fetching {website_url} for '{school_name}': {e}")
            else:
                logging.info(f"Skipping row {index} due to invalid or missing URL.")

    finally:
        # Close the browser
        driver.quit()

    output_csv = 'kingston_catholic_schools_with_emails.csv'
    df.to_csv(output_csv, index=False)
    logging.info(f"Email extraction complete. Updated CSV saved as '{output_csv}'.")

if __name__ == '__main__':
    main()