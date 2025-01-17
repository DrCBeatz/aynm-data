import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# NEW: for handling dropdown and explicit waits
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    # 1) Initialize the Selenium WebDriver
    service = Service()  # <-- Adjust this path to your local chromedriver if needed
    driver = webdriver.Chrome(service=service)
    
    driver.get("https://www.scdsb.on.ca/cms/One.aspx?portalId=210982&pageId=739105")
    
    # 2) Select the "All" option in the dropdown
    select_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctl17_ddlResultPerPage")
    dropdown = Select(select_element)
    dropdown.select_by_value("10000")  # "All" has value="10000"
    
    # --------------------------------------------------------------------
    # Option A (simple): Just sleep for a few seconds to let the page reload
    # time.sleep(5)
    #
    # Option B (better): Use an explicit wait to wait for the new rows to appear
    # --------------------------------------------------------------------
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            "#ctl00_ContentPlaceHolder1_ctl17_gridView tr.grid_row, "
            "#ctl00_ContentPlaceHolder1_ctl17_gridView tr.grid_row_alt"
        ))
    )
    
    # 3) Now locate all table rows (excluding the header) after the page updates
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "#ctl00_ContentPlaceHolder1_ctl17_gridView tr.grid_row, "
        "#ctl00_ContentPlaceHolder1_ctl17_gridView tr.grid_row_alt"
    )
    
    # Prepare a list to hold the scraped data
    all_data = []
    
    for row in rows:
        # Each row has 6 <td> cells in order:
        # 0: Name
        # 1: Address
        # 2: Postal Code
        # 3: Classification
        # 4: Website
        # 5: Municipality (not needed for our final CSV)
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 6:
            continue
        
        # Extract School (Name)
        school_name = cells[0].text.strip()
        
        # Extract Address + Postal Code
        address = cells[1].text.strip()
        postal_code = cells[2].text.strip()
        full_address = f"{address}, {postal_code}"
        
        # Extract Grade (Classification)
        grade = cells[3].text.strip()
        
        # Extract Website
        website_elem = cells[4].find_element(By.TAG_NAME, "a")
        website_url = website_elem.get_attribute("href")
        
        # Since phone is not in the HTML table, we use "N/A"
        phone = "N/A"
        
        # Build a dictionary for this row
        row_data = {
            "School": school_name,
            "Address": full_address,
            "Grade": grade,
            "Phone": phone,
            "Website": website_url
        }
        all_data.append(row_data)
    
    # 4) Convert list of dicts to a Pandas DataFrame
    df = pd.DataFrame(all_data, columns=["School", "Address", "Grade", "Phone", "Website"])
    
    # 5) Save the DataFrame to CSV
    df.to_csv("scdsb_schools.csv", index=False, encoding="utf-8")
    print("Data saved to 'scdsb_schools.csv'")
    
    # 6) Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
