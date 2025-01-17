import time
import pandas as pd
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# -------------------------------------------------------------------
# 1. Set up the list of URLs to scrape
# -------------------------------------------------------------------
school_urls = [
    "https://csviamonde.ca/nos-ecoles/trouver-une-ecole/fiche-ecole/ecole-elementaire-lamarsh",
    "https://csviamonde.ca/nos-ecoles/trouver-une-ecole/fiche-ecole/ecole-elementaire-lheritage",
    "https://csviamonde.ca/nos-ecoles/trouver-une-ecole/fiche-ecole/ecole-elementaire-nouvel-horizon",
    "https://csviamonde.ca/nos-ecoles/trouver-une-ecole/fiche-ecole/ecole-elementaire-franco-niagara",
    "https://csviamonde.ca/ecole-secondaire-franco-niagara"
]

# -------------------------------------------------------------------
# 2. Initialize Selenium WebDriver
#    (Adjust this path to your ChromeDriver or preferred driver)
# -------------------------------------------------------------------
service = Service()  # <-- UPDATE PATH
driver = webdriver.Chrome(service=service)

# OPTIONAL: You can maximize the browser window, or run headless, etc.
# driver.maximize_window()

# A helper function to extract data from a single school page
def extract_school_info(url):
    """
    Visits the given url, extracts the required fields, and returns
    a dictionary with the results.
    """
    # Go to the page
    driver.get(url)
    time.sleep(2)  # Let the page load; adjust if needed
    
    # Initialize storage with defaults (in case something isn't found)
    school_name = ""
    phone = ""
    principal_name = ""
    principal_email = ""
    address = ""
    website = ""

    # Retrieve the raw page source (useful for commented-out HTML)
    page_source = driver.page_source

    # A) School name
    try:
        school_elem = driver.find_element(By.CSS_SELECTOR, ".content-centered-title-text")
        school_name = school_elem.text.strip()
    except NoSuchElementException:
        pass

    # B) Phone
    #    The phone is typically in the first li.icon-list-element with text
    try:
        phone_elem = driver.find_element(
            By.CSS_SELECTOR,
            "li.icon-list-element span.icon-list-element-text"
        )
        phone = phone_elem.text.strip()
    except NoSuchElementException:
        pass

    # C) Principal name and email
    #    Look for "Direction" under "Contactez-nous"
    try:
        principal_element = driver.find_element(
            By.XPATH,
            '//span[@class="description-subtitle" and (text()="Direction")]/following-sibling::span[@class="description-name"]'
        )
        principal_name = principal_element.text.strip()
        # The child <a> has the 'mailto' link
        principal_email_element = principal_element.find_element(By.TAG_NAME, "a")
        principal_email = principal_email_element.get_attribute("href").replace("mailto:", "").strip()
    except NoSuchElementException:
        pass

    # D) Address
    #    Under "Coordonnées de l'école" -> <span class="description-adress">
    try:
        address_elem = driver.find_element(By.CSS_SELECTOR, "span.description-adress")
        address = address_elem.text.replace("\n", ", ").strip()
    except NoSuchElementException:
        pass

    # E) Website
    #    Method 1: Grab the Facebook link if present
    try:
        facebook_element = driver.find_element(
            By.XPATH,
            '//div[@class="description-element"]/span[@class="description-subtitle" and text()="Facebook"]/following-sibling::span/a'
        )
        facebook_link = facebook_element.get_attribute("href").strip()
    except NoSuchElementException:
        facebook_link = ""

    #    Method 2 (optional): Extract official site from commented-out HTML
    #    We look for something like: <a href="http://csviamonde.ca/ecoles/..."> in a comment
    match = re.search(
        r'<!--div.*<a href="([^"]+)"[^>]*>Visiter le site web de l&#039;école</a>.*-->',
        page_source,
        re.DOTALL
    )
    if match:
        official_site = match.group(1).strip()
    else:
        official_site = ""

    #    Decide which link to use as "Website"
    if official_site:
        website = official_site
    else:
        website = facebook_link

    # Return as a dictionary
    return {
        "School": school_name,
        "Website": website,
        "Principal": principal_name,
        "Address": address,
        "Phone": phone,
        "Email": principal_email
    }

# -------------------------------------------------------------------
# 3. Loop through all school URLs and store results
# -------------------------------------------------------------------
all_schools_data = []

for url in school_urls:
    print(f"Processing: {url}")
    info = extract_school_info(url)
    all_schools_data.append(info)

# -------------------------------------------------------------------
# 4. Create a DataFrame and write to CSV
# -------------------------------------------------------------------
df = pd.DataFrame(all_schools_data)
df.to_csv("niagara_french_schools_contact.csv", index=False, encoding="utf-8")

# -------------------------------------------------------------------
# 5. Close the driver
# -------------------------------------------------------------------
driver.quit()

print("Extraction complete! The CSV file 'niagara_french_schools_contact.csv' has been created.")
