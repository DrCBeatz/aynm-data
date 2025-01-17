import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re

# 1) List of CSC MonAvenir school URLs to scrape
school_urls = [
    "https://cscmonavenir.ca/ecole/ecole-secondaire-catholique-saint-jean-de-brebeuf-welland/ecole-elementaire-catholique-du-sacre-coeur-welland/",
    "https://cscmonavenir.ca/ecole/ecole-secondaire-catholique-saint-jean-de-brebeuf-welland/ecole-elementaire-catholique-immaculee-conception-st-catharines/",
    "https://cscmonavenir.ca/ecole/ecole-secondaire-catholique-saint-jean-de-brebeuf-welland/ecole-elementaire-catholique-notre-dame-de-la-jeunesse-niagara-falls/",
    "https://cscmonavenir.ca/ecole/ecole-secondaire-catholique-saint-jean-de-brebeuf-welland/ecole-elementaire-catholique-saint-antoine-niagara-falls/",
    "https://cscmonavenir.ca/ecole/ecole-secondaire-catholique-saint-jean-de-brebeuf-welland/ecole-elementaire-catholique-saint-francois-dassise-welland/",
    "https://cscmonavenir.ca/ecole/ecole-secondaire-catholique-saint-jean-de-brebeuf-welland/ecole-elementaire-catholique-sainte-marguerite-bourgeoys-st-catharines/"
]


def extract_school_info(driver, url):
    """
    Given a Selenium driver and the URL of a CSC MonAvenir school page,
    extracts School, Website, Principal, Address, Phone, Email (Principal's email).
    Returns a dict of these fields.
    """
    info = {
        "School": "",
        "Website": "",
        "Principal": "",
        "Address": "",
        "Phone": "",
        "Email": ""
    }

    # Go to the page
    driver.get(url)
    time.sleep(2)  # Adjust if needed; or use WebDriverWait for more robust waiting

    try:
        # A) School name 
        #    <header class="page-header"><h1>...</h1>
        school_elem = driver.find_element(By.CSS_SELECTOR, "header.page-header > h1")
        info["School"] = school_elem.text.strip()
    except NoSuchElementException:
        pass

    # B) Website 
    #    The "Site Internet" button is typically: <a>Site Internet</a>
    try:
        site_internet_elem = driver.find_element(
            By.XPATH,
            '//div[contains(@class,"row")]//a[contains(text(), "Site Internet")]'
        )
        info["Website"] = site_internet_elem.get_attribute("href")
    except NoSuchElementException:
        pass

    # C) Principal + Email
    #    Under “Contactez-nous” -> The first <a> in that paragraph is typically the principal
    try:
        contact_p = driver.find_element(
            By.XPATH,
            '//h2[contains(text(),"Contactez-nous")]/following-sibling::p'
        )
        # The principal is usually the first link in that paragraph
        principal_link = contact_p.find_element(By.TAG_NAME, "a")
        info["Principal"] = principal_link.text.strip()

        # The principal’s email is the link’s "mailto:"
        info["Email"] = principal_link.get_attribute("href").replace("mailto:", "").strip()
    except NoSuchElementException:
        pass

    # D) Address
    #    Found in <address> ... 
    #    e.g., 
    #    310, rue Fitch
    #    Welland (Ontario) L3C 4W5
    #    Tél. : 905-...
    #    Téléc. : 905-...
    try:
        address_elem = driver.find_element(By.CSS_SELECTOR, "address")
        address_text = address_elem.text.strip()
        # Example text lines:
        #    310, rue Fitch
        #    Welland (Ontario) L3C 4W5
        #    Tél. : 905-734-8133
        #    Téléc. : 905-734-9385
        # We parse out phone separately.

        # E) Phone -> <a href="tel:..."> in the address
        #    We'll look for the first phone link that has "tel:"
        phone_link = address_elem.find_element(By.XPATH, './/a[contains(@href,"tel:")]')
        info["Phone"] = phone_link.text.strip()

        # Remove lines that start with "Tél." or "Téléc." to isolate address lines only
        lines = [
            line for line in address_text.splitlines()
            if not line.strip().startswith(("Tél.", "Téléc."))
        ]
        clean_address = ", ".join(line.strip() for line in lines if line.strip())
        info["Address"] = clean_address
    except NoSuchElementException:
        pass

    return info


def main():
    # 1) Initialize Selenium WebDriver
    service = Service()  # <-- Replace with your actual driver path
    driver = webdriver.Chrome(service=service)

    all_data = []

    for url in school_urls:
        print(f"Extracting data from: {url}")
        school_data = extract_school_info(driver, url)
        all_data.append(school_data)

    # Convert the list of dicts to a DataFrame
    df = pd.DataFrame(all_data)

    # 2) Save the DataFrame to CSV
    df.to_csv("csc_monavenir_schools.csv", index=False, encoding="utf-8")
    print("Data saved to 'csc_monavenir_schools.csv'")

    # 3) Close the browser
    driver.quit()


if __name__ == "__main__":
    main()
