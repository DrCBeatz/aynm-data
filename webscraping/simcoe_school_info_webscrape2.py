import time
import re
import logging
import pandas as pd
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def do_scrape(driver) -> Tuple[str, str, str]:
    """
    From the current page in `driver`, extract:
      - phone (from the "School details" table),
      - principal (from the "School contacts" section),
      - email (from a mailto: link or fallback).
    Returns a tuple (phone, principal, email).
    Raises if key elements cannot be found.
    """
    time.sleep(2)  # Simple wait for the page to load

    # -----------------------------------------------------------
    # 1) Extract phone from "School details" table
    # -----------------------------------------------------------
    try:
        details_table = driver.find_element(
            By.XPATH,
            "//h3[contains(translate(text(), 'SCHOOL DETAILS', 'school details'), 'school details')]/following::table[1]"
        )
        table_text = details_table.text
    except Exception:
        table_text = ""

    phone_pattern = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]\d{4}")
    phones_found = phone_pattern.findall(table_text)
    phone = phones_found[0] if phones_found else "Not found"

    # -----------------------------------------------------------
    # 2) Extract principal from "School contacts" area
    # -----------------------------------------------------------
    try:
    # Find the <div> that has an <h3> containing "School contacts"
        contacts_div = driver.find_element(
            By.XPATH,
            "//div[h3[contains(translate(text(), 'SCHOOL CONTACTS', 'school contacts'), 'school contacts')]]"
        )
        
        # Find the <p> that has <strong> containing "Principal"
        principal_p = contacts_div.find_element(
            By.XPATH,
            ".//p[strong[contains(translate(text(), 'PRINCIPAL', 'principal'), 'principal')]]"
        )
        
        # Check if principal_p has both the word "Principal" and a second line
        principal_text = principal_p.text.strip()
        lines = principal_text.splitlines()
        
        if len(lines) > 1:
            # If there's more than one line, the second line might be the name
            principal = lines[1].strip()
        else:
            # Otherwise, let's look at the next sibling <p> as the name
            try:
                next_p = principal_p.find_element(By.XPATH, "following-sibling::p[1]")
                principal = next_p.text.strip()
            except Exception:
                # fallback if no next sibling
                principal = "Not found"
                
        # If there's extra text like "Principal" in `principal`, remove it
        if principal.lower().startswith("principal"):
            principal = principal.replace("Principal", "").strip()

    except Exception:
        principal = "Not found"


    # -----------------------------------------------------------
    # 3) Extract email
    # -----------------------------------------------------------
    try:
        email_a = driver.find_element(By.XPATH, "//a[contains(@href, 'mailto:')]")
        email = email_a.text.strip()
    except Exception:
        page_text = driver.page_source
        email_pattern = re.compile(r"[\w\.-]+@scdsb\.on\.ca", re.IGNORECASE)
        emails_found = email_pattern.findall(page_text)
        email = emails_found[0] if emails_found else "Not found"

    return phone, principal, email

def scrape_school_info(driver, base_url: str) -> Tuple[str, str, str]:
    """
    Reuses the browser `driver` to scrape phone, principal, and email.
    1) First tries base_url + "/our_school/school_information".
    2) If that fails, tries base_url + "/Classes/school_information".
    Returns (phone, principal, email).
    """
    phone, principal, email = ("Not found", "Not found", "Not found")

    paths_to_try = [
        "/our_school/school_information",
        "/Classes/school_information",
    ]
    for path in paths_to_try:
        try:
            url = base_url.rstrip("/") + path
            driver.get(url)
            phone, principal, email = do_scrape(driver)
            # If do_scrape succeeds, we're done
            return phone, principal, email
        except Exception:
            # If we fail, loop to the next path
            pass

    return phone, principal, email

def main():
    # -------------------------------------------------------
    # Configure logging
    # -------------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("Starting the scraping process...")

    # 1) Start a SINGLE WebDriver session
    service = Service()
    driver = webdriver.Chrome(service=service)

    # 2) Load your existing CSV into a DataFrame
    df = pd.read_csv("scdsb_schools.csv")

    # Ensure columns exist in the DataFrame
    for col in ["Phone", "Principal", "Email"]:
        if col not in df.columns:
            df[col] = ""

    # 3) Iterate through each row
    for idx in range(len(df)):
        base_url = df.loc[idx, "Website"]

        # If there's no valid URL, skip
        if not isinstance(base_url, str) or not base_url.startswith("http"):
            logging.warning(f"Row {idx}: Invalid URL '{base_url}'. Skipping.")
            continue

        logging.info(f"Row {idx}: Scraping {base_url}...")
        phone, principal, email = scrape_school_info(driver, base_url)

        # Log the data we’re about to store
        logging.info(
            f"Row {idx} data found => Phone: {phone}, Principal: {principal}, Email: {email}"
        )

        # Update DataFrame
        df.loc[idx, "Phone"] = phone
        df.loc[idx, "Principal"] = principal
        df.loc[idx, "Email"] = email

    # 4) Close the browser
    driver.quit()
    logging.info("Browser session ended.")

    # 5) Save the updated DataFrame
    final_columns = ["School", "Address", "Grade", "Phone", "Website", "Principal", "Email"]
    df = df[final_columns]
    df.to_csv("scdsb_schools_updated.csv", index=False, encoding="utf-8")

    logging.info("Updated data saved to 'scdsb_schools_updated.csv'")

if __name__ == "__main__":
    main()
