from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def wait_for_element(driver, by, locator, timeout=10):
    """
    Wait up to `timeout` seconds for an element to appear.
    Returns the element if found, or None if not found/times out.
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
    except (TimeoutException, NoSuchElementException):
        return None

def fetch_school_details(driver, details_url):
    """
    Given an already-open Selenium WebDriver and a details URL,
    navigate to the page and scrape Grade, Address, Phone,
    Principal Name, and Principal Email. Returns a dict of results.
    """
    results = {
        "Grade": "N/A",
        "Address": "N/A",
        "Phone": "N/A",
        "Principal": "N/A",
        "Email": "N/A"
    }

    try:
        driver.get(details_url)

        # 1) GRADE
        grade_element = wait_for_element(
            driver,
            By.XPATH,
            '//th[normalize-space(text())="Grade "]/following-sibling::tr/td',
            timeout=10
        )
        if grade_element:
            results["Grade"] = grade_element.text.strip()

        # 2) ADDRESS & PHONE (in the left column <td class="hdsb-column-left">)
        left_col_element = wait_for_element(
            driver,
            By.CSS_SELECTOR,
            'td.hdsb-column-left .SearchResultDetailSchool',
            timeout=10
        )
        if left_col_element:
            lines = left_col_element.text.splitlines()
            # Example snippet might have:
            # [
            #   'Abbey Park High School',
            #   '', 
            #   '1455 Glen Abbey Gate ',
            #   'Oakville, L6M 2G5',
            #   'Phone: 905-827-4101',
            #   'Fax: 905-825-5265',
            #   ...
            # ]
            # Indices can vary, so be flexible.

            # Attempt to extract address lines (commonly index 3 & 4 in the snippet)
            if len(lines) >= 5:
                address_line_1 = lines[3].strip()
                address_line_2 = lines[4].strip()
                results["Address"] = f"{address_line_1}, {address_line_2}"

            # Find phone line that starts with "Phone:"
            phone_line = next((l for l in lines if l.startswith("Phone:")), None)
            if phone_line:
                results["Phone"] = phone_line.replace("Phone:", "").strip()

        # 3) PRINCIPAL NAME & EMAIL
        # In the snippet, the Principal is the first <a> in the <div class="SchoolDetailedInfo">
        principal_anchor = wait_for_element(
            driver,
            By.XPATH,
            '//div[@class="SchoolDetailedInfo"]/a[1]',
            timeout=10
        )
        if principal_anchor:
            results["Principal"] = principal_anchor.text.strip()
            mailto_href = principal_anchor.get_attribute("href")
            if mailto_href and mailto_href.startswith("mailto:"):
                results["Email"] = mailto_href.replace("mailto:", "").strip()

    except Exception as e:
        print(f"Error fetching details for URL {details_url}: {e}")
        # Keep the default "N/A" values if something fails

    return results

def main():
    # 1) Load the CSV with school data (including the 'Details' column)
    df = pd.read_csv("halton_district_schoolboard.csv")

    # 2) Add new columns (if they don’t exist yet)
    for col in ["Grade", "Address", "Phone", "Principal", "Email"]:
        if col not in df.columns:
            df[col] = None

    # 3) Set up the Selenium driver (Chrome in this example)
    # If you need a specific path to ChromeDriver, do:
    # service = Service("path/to/chromedriver")
    # driver = webdriver.Chrome(service=service)
    driver = webdriver.Chrome()

    try:
        # 4) Iterate over each row in the DataFrame
        for i, row in df.iterrows():
            details_url = row["Details"]  # Name of the column containing the URL
            if pd.isna(details_url) or not isinstance(details_url, str):
                # If no valid URL, skip or set N/A
                df.at[i, "Grade"] = "N/A"
                df.at[i, "Address"] = "N/A"
                df.at[i, "Phone"] = "N/A"
                df.at[i, "Principal"] = "N/A"
                df.at[i, "Email"] = "N/A"
                continue

            # 5) Fetch the data from the details page
            scraped_data = fetch_school_details(driver, details_url)

            # 6) Update the DF with the scraped data
            df.at[i, "Grade"] = scraped_data["Grade"]
            df.at[i, "Address"] = scraped_data["Address"]
            df.at[i, "Phone"] = scraped_data["Phone"]
            df.at[i, "Principal"] = scraped_data["Principal"]
            df.at[i, "Email"] = scraped_data["Email"]

    finally:
        # 7) Quit the driver
        driver.quit()

    # 8) Save updated DataFrame to a new CSV
    df.to_csv("halton_district_schoolboard_updated.csv", index=False)
    print("Scraping complete. Results saved to halton_district_schoolboard_updated.csv")

if __name__ == "__main__":
    main()
