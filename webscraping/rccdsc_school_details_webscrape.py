import pandas as pd
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def extract_school_details(driver, url):
    """
    Given a URL for a school's info page, uses Selenium to load the page and parse the final DOM. 
    Extracts Address, Phone, Email, and Principal. Prints debug info for email extraction.
    """
    details = {
        "Address": "",
        "Phone": "",
        "Email": "",
        "Principal": ""
    }

    print(f"DEBUG: Fetching {url}")

    try:
        driver.get(url)
        # Optionally wait a few seconds if needed for dynamic elements:
        time.sleep(2)
    except Exception as e:
        print(f"ERROR: Failed to retrieve {url} due to {e}")
        return details

    # Grab the final rendered HTML from Selenium
    page_html = driver.page_source
    print(f"DEBUG: Raw HTML snippet for {url}")
    print(page_html[:2000])  # Print first 2k chars for debug

    soup = BeautifulSoup(page_html, "html.parser")

    # Helper function (unchanged) ---------------------------------
    def find_heading_sibling_text(heading_regex):
        heading_tag = soup.find(
            lambda tag: tag.name in ["h2", "h3"] 
                        and re.search(heading_regex, tag.get_text(strip=True), re.IGNORECASE)
        )
        if not heading_tag:
            return ""
        
        next_text_div = None
        heading_wrapper = heading_tag.find_parent("div", class_="elementor-widget-heading")
        if heading_wrapper:
            next_text_div = heading_wrapper.find_next_sibling("div", class_="elementor-widget-text-editor")
        if not next_text_div:
            next_text_div = heading_tag.find_next("div", class_="elementor-widget-text-editor")

        if not next_text_div:
            return ""

        text = next_text_div.get_text(separator=" ").strip()
        return text
    # -------------------------------------------------------------

    # Address extraction
    address_text = find_heading_sibling_text(r"^address[:]?$")
    details["Address"] = address_text if address_text else ""

    # Phone extraction
    phone_tag = soup.find("a", href=re.compile(r"^tel:", re.IGNORECASE))
    if phone_tag:
        details["Phone"] = phone_tag.get_text(strip=True)
    
    # -----------------------------------------------------------------
    # DEBUG LOGGING FOR EMAIL EXTRACTION
    # -----------------------------------------------------------------
    mailto_links = soup.select('a[href^="mailto:"]')
    print(f"DEBUG: Found {len(mailto_links)} <a> tags with href starting 'mailto:' on {url}")
    extracted_email = ""
    for link in mailto_links:
        mailto_href = link.get("href", "")
        # example: "mailto:cat.administration@rccdsb.ca"
        # we can parse out the actual email
        possible_email = mailto_href.replace("mailto:", "").strip()

        # If we want to skip "inquiry@rccdsb.ca" or "HelpHelp",
        # we can check conditions:
        if "inquiry@rccdsb.ca" in possible_email:
            # This is the generic "HelpHelp" link - skip it
            continue

        # We found a link that isn't the "inquiry" one, so let's use it
        extracted_email = possible_email
        break  # stop after the first real one

    print(f"DEBUG:  => Extracted email: {extracted_email}")
    details["Email"] = extracted_email
    # Principal extraction
    principal_text = find_heading_sibling_text(r"^principal[:]?$")
    details["Principal"] = principal_text if principal_text else ""

    return details


def main():
    # Configure Selenium (Chrome in headless mode here)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # If needed, specify the path to your chromedriver, e.g. executable_path="/path/to/chromedriver"
    driver = webdriver.Chrome(options=chrome_options)

    df_schools = pd.read_csv("schools.csv")

    addresses = []
    phones = []
    emails = []
    principals = []

    for index, row in df_schools.iterrows():
        school_name = row["School Name"]
        school_url = row["URL"]
        print(f"\nPROCESSING: {school_name} -> {school_url}")

        results = extract_school_details(driver, school_url)
        addresses.append(results["Address"])
        phones.append(results["Phone"])
        emails.append(results["Email"])
        principals.append(results["Principal"])

    df_result = pd.DataFrame({
        "School Name": df_schools["School Name"],
        "URL": df_schools["URL"],
        "Address": addresses,
        "Phone": phones,
        "Email": emails,
        "Principal": principals
    })

    df_result.to_csv("schools_with_details.csv", index=False)
    print("\nExtraction complete! Saved to 'schools_with_details.csv'.")

    # Close the browser when done
    driver.quit()


if __name__ == "__main__":
    main()