import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# For explicit waits:
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    # ------------------------------------------------
    # 1. Load the initial CSV into a pandas DataFrame
    # ------------------------------------------------
    csv_input = "hamilton_wentworth_schools.csv"  # Example CSV name
    df = pd.read_csv(csv_input)

    # Make sure your CSV has columns named "School" and "Website".
    # We'll add new columns to store the scraped data.
    df["Address"] = ""
    df["Phone"] = ""
    df["Principal"] = ""
    df["Email"] = ""

    # ------------------------------------------------
    # 2. Set up Selenium WebDriver with WebDriverWait
    # ------------------------------------------------
    service = Service()
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)  # timeout of 10 seconds for each element

    # ------------------------------------------------
    # 3. Iterate through each school website and scrape data
    # ------------------------------------------------
    for i, row in df.iterrows():
        school_name = row["School"]
        website = row["Website"]
        
        if not isinstance(website, str) or not website.startswith("http"):
            print(f"Skipping invalid URL for {school_name}: {website}")
            continue

        print(f"Scraping: {school_name} -> {website}")
        
        try:
            driver.get(website)

            # Wait for elements to appear on the page, then extract
            # Address
            address_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.address"))
            )
            address = address_element.text

            # Phone
            phone_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.phone"))
            )
            phone = phone_element.text

            # Email
            email_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.email"))
            )
            email = email_element.text

            # Principal
            principal_heading = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='heading'][text()='Principal']")
                )
            )
            principal_element = principal_heading.find_element(
                By.XPATH, "./following-sibling::div"
            )
            principal = principal_element.text

            # Store in the DataFrame
            df.at[i, "Address"] = address
            df.at[i, "Phone"] = phone
            df.at[i, "Email"] = email
            df.at[i, "Principal"] = principal

        except Exception as e:
            print(f"Failed to scrape {school_name} ({website}): {e}")

    # ------------------------------------------------
    # 4. Close the browser
    # ------------------------------------------------
    driver.quit()

    # ------------------------------------------------
    # 5. Save the results to a new CSV
    # ------------------------------------------------
    csv_output = "hamilton_wentworth_schools_updated.csv"
    df.to_csv(csv_output, index=False)
    print(f"Scraped data saved to: {csv_output}")

if __name__ == "__main__":
    main()
