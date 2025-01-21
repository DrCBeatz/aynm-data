from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def wait_for_element(driver, by, locator, timeout=10):
    """
    Helper function to wait up to `timeout` seconds for an element.
    Returns the element if found, or None if not found within `timeout` seconds.
    """
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        return elem
    except (TimeoutException, NoSuchElementException):
        return None

def scrape_school_details():
    # URL of the school details page you want to parse
    details_page = "http://www.hdsb.ca/schooldetails/SchoolDetails.aspx?sc=2002"

    # If you prefer to specify a chromedriver service:
    # service = Service("path/to/chromedriver")
    # driver = webdriver.Chrome(service=service)
    # Otherwise, just create the driver directly:
    driver = webdriver.Chrome()

    try:
        driver.get(details_page)

        # -----------------------------------------------------------
        # 1) Extract the GRADE
        # -----------------------------------------------------------
        # Example XPATH: <th>Grade </th> -> the next <td> = '9 - 12'
        grade_element = wait_for_element(
            driver, 
            By.XPATH, 
            '//th[normalize-space(text())="Grade "]/following-sibling::tr/td',
            timeout=10
        )
        if grade_element:
            grade = grade_element.text.strip()
        else:
            grade = "N/A"   # or handle differently

        # -----------------------------------------------------------
        # 2) Extract ADDRESS & PHONE
        # -----------------------------------------------------------
        left_col_element = wait_for_element(
            driver,
            By.CSS_SELECTOR, 
            'td.hdsb-column-left .SearchResultDetailSchool',
            timeout=10
        )
        address = "N/A"
        phone = "N/A"

        if left_col_element:
            lines = left_col_element.text.splitlines()
            # Based on your snippet, we expect:
            # [ 'Abbey Park High School', '', '1455 Glen Abbey Gate ', ... ]
            # But the indices may shift if the content changes.

            # Attempt to extract lines carefully
            if len(lines) >= 5:
                address_line_1 = lines[3].strip()
                address_line_2 = lines[4].strip()
                address = f"{address_line_1}, {address_line_2}"

            # Find phone line
            phone_line = next((l for l in lines if l.startswith("Phone:")), None)
            if phone_line:
                phone = phone_line.replace("Phone:", "").strip()

        # -----------------------------------------------------------
        # 3) Extract PRINCIPAL & EMAIL
        # -----------------------------------------------------------
        # The first <a> in div.SchoolDetailedInfo is the principal
        principal_anchor = wait_for_element(
            driver,
            By.XPATH,
            '//div[@class="SchoolDetailedInfo"]/a[1]',
            timeout=10
        )
        if principal_anchor:
            principal_name = principal_anchor.text.strip()
            principal_email = principal_anchor.get_attribute("href").replace("mailto:", "").strip()
        else:
            principal_name = "N/A"
            principal_email = "N/A"

        # -----------------------------------------------------------
        # 4) Store data in a pandas DataFrame
        # -----------------------------------------------------------
        data = {
            "Grade": grade,
            "Address": address,
            "Phone": phone,
            "Principal": principal_name,
            "Email": principal_email
        }
        df = pd.DataFrame([data])

        # Print or save
        print(df)
        # df.to_csv("school_details.csv", index=False)

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_school_details()
