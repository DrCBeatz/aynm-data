import logging
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def scrape_school_details_selenium(driver, profile: str, url_domain: str) -> dict:
    """
    Given an existing Selenium WebDriver ('driver'), navigate to url_domain + profile
    and scrape:
      - 'Address 1' (Street Address)
      - 'Phone'
      - 'Email'
    Skipping 'Website' row to avoid offset issues.

    Returns a dict: {
        "Street Address": <value or None>,
        "Phone": <value or None>,
        "Email": <value or None>
    }
    """
    # Construct the full URL
    full_url = url_domain + profile
    logging.info(f"Navigating to URL: {full_url}")

    results = {
        "Street Address": None,
        "Phone": None,
        "Email": None
    }

    # 1) Load the page
    driver.get(full_url)

    # 2) Wait up to 10s for at least one <td class="datatitle"> to appear
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.datatitle")))

    # Small pause to allow any dynamic JS to complete
    time.sleep(1)

    # 3) Find all table rows
    rows = driver.find_elements(By.CSS_SELECTOR, "tr")
    logging.debug(f"Found {len(rows)} <tr> elements.")

    # We'll map label → value pairs
    label_value_map = {}

    for row in rows:
        label_cells = row.find_elements(By.CSS_SELECTOR, "td.datatitle")
        pager_cells = row.find_elements(By.CSS_SELECTOR, "td.pager")
        if not label_cells:
            # Not a label row
            continue

        label_text = label_cells[0].text.strip()
        if not pager_cells:
            # No value in the same row
            logging.debug(f"Row has label '{label_text}' but no pager cell found.")
            continue

        value_text = pager_cells[0].text.strip()
        logging.debug(f"Label: '{label_text}' -> Value: '{value_text}'")

        if label_text.lower().startswith("website"):
            # Skip the 'Website' row to avoid offset
            logging.debug("Skipping 'Website' row.")
            continue

        label_value_map[label_text] = value_text

    # 4) Pull out desired fields
    results["Street Address"] = label_value_map.get("Address 1", None)
    results["Phone"] = label_value_map.get("Phone", None)
    results["Email"] = label_value_map.get("Email", None)

    logging.debug(f"Scraped data: {results}")
    return results


def main():
    # 1) Load the CSV file
    csv_file = "canadian_accredited_independent_schools.csv"
    df = pd.read_csv(csv_file)
    logging.info(f"Loaded CSV with {len(df)} rows.")

    # 2) Add 3 new columns for the data we plan to scrape
    df["Street Address"] = None
    df["Phone"] = None
    df["Email"] = None

    # 3) Initialize Selenium (Chrome) only once
    chrome_options = Options()
    # Uncomment to run in headless mode:
    # chrome_options.add_argument("--headless")

    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 4) Iterate over each row, scrape the data, and store it
        url_domain = "https://www.cais.ca/"
        for index, row in df.iterrows():
            profile = str(row["Profile"])  # e.g. "page.cfm?p=2424&start=1"
            logging.info(f"Processing row {index} with Profile='{profile}'")

            # If the profile path is invalid or "N/A", skip
            if not profile or profile == "N/A":
                logging.warning(f"No valid profile path for row {index}. Skipping.")
                continue

            # Scrape data (reusing the same driver)
            details = scrape_school_details_selenium(driver, profile, url_domain)

            # Update DataFrame
            df.at[index, "Street Address"] = details["Street Address"]
            df.at[index, "Phone"] = details["Phone"]
            df.at[index, "Email"] = details["Email"]

    finally:
        # 5) Quit the browser once we're done with all rows
        driver.quit()

    # 6) Optionally save the updated DataFrame to a new CSV
    output_csv = "canadian_accredited_independent_schools_with_contact.csv"
    df.to_csv(output_csv, index=False)
    logging.info(f"Saved updated data to {output_csv}")


if __name__ == "__main__":
    main()
