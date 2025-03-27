# yamaha_b2b_webscrape.py

# Script for webscraping product information from Yamaha B2B website and saving
# as CSV format suitable for importing into Shopify

WAIT_TIME = 10  # seconds
ALLOW, BLOCK = 1, 2
HEADLESS = False

import time
import pandas as pd
from decouple import config

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

# ------------------------------------------------------------------------------
# 1. Set Chrome Options
# ------------------------------------------------------------------------------
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-infobars")
if HEADLESS:
    chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option(
    "prefs",
    {
        "profile.default_content_setting_values.media_stream_mic": BLOCK,
        "profile.default_content_setting_values.media_stream_camera": BLOCK,
        "profile.default_content_setting_values.geolocation": BLOCK,
        "profile.default_content_setting_values.notifications": BLOCK,
    },
)

# ------------------------------------------------------------------------------
# 2. Configure Inputs & Outputs
# ------------------------------------------------------------------------------
input_file = ""
output_file = "yamaha_webscrape_output.csv"
user_name = config("YAMAHA_B2B_USERNAME")
password = config("YAMAHA_B2B_PASSWORD")
url = "https://mus.ca.yamaha.com/s/login/?language=en_US"

# ------------------------------------------------------------------------------
# 3. Prepare Product List
# ------------------------------------------------------------------------------
if input_file:
    # If we have an input CSV, read the SKUs from there
    product_df = pd.read_csv(input_file)
    product_list = product_df["Variant SKU"].tolist()
else:
    # Fallback: define products directly here
    product_list = ["YAS26", "YAS280"]  # Example

print(f"Scraping data for {len(product_list)} products:")
for product in product_list:
    print(f"  {product}")

# ------------------------------------------------------------------------------
# 4. Initialize WebDriver
# ------------------------------------------------------------------------------
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()  # You can comment this out if you prefer smaller window

print(f"Opening {url} in Chrome browser...")
driver.get(url)
wait = WebDriverWait(driver, WAIT_TIME)

# ------------------------------------------------------------------------------
# 5. Log In
# ------------------------------------------------------------------------------
try:
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "54:2;a")))
    email_input.clear()
    email_input.send_keys(user_name)
except Exception as e:
    print("Could not find the email input:", e)

try:
    password_input = wait.until(EC.visibility_of_element_located((By.ID, "67:2;a")))
    password_input.clear()
    password_input.send_keys(password)
except Exception as e:
    print("Could not find the password input:", e)

try:
    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.loginButton"))
    )
    login_button.click()
except Exception as e:
    print("Could not find or click the login button:", e)

# ------------------------------------------------------------------------------
# 6. Iterate Over Products
# ------------------------------------------------------------------------------
products_not_found_list = []
rows = []  # We'll store [product, MAP, WSP] here

for product in product_list:
    # --------------------------------------------------------------------------
    # 6a. Go to search input, enter product SKU
    # --------------------------------------------------------------------------
    try:
        search_input = WebDriverWait(driver, WAIT_TIME).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.search-input-with-button"))
        )
        search_input.clear()
        search_input.send_keys(product)
        search_input.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"[{product}] Could not perform search:", e)
        products_not_found_list.append(product)
        # We'll store a row with None data, or skip entirely
        rows.append([product, None, None])  
        continue

    # --------------------------------------------------------------------------
    # 6b. Click product link
    # --------------------------------------------------------------------------
    xpath_link = f"//span[@part='formatted-rich-text' and text()='{product}']/ancestor::a[1]"
    try:
        product_link = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, xpath_link))
        )
        product_link.click()
    except Exception as e:
        print(f"[{product}] Could not find/click product link:", e)
        products_not_found_list.append(product)
        rows.append([product, None, None])
        continue

    # --------------------------------------------------------------------------
    # 6c. Wait for details to load
    # --------------------------------------------------------------------------
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "b2b_buyer_product_details-summary"))
        )
        
        time.sleep(2)
    except TimeoutException:
        print(f"[{product}] Timed out waiting for product details to load.")
        products_not_found_list.append(product)
        rows.append([product, None, None])
        continue

    # --------------------------------------------------------------------------
    # 6d. Grab MAP
    # --------------------------------------------------------------------------
    try:
        map_xpath = (
            "("
            "//b2b_buyer_product_details-heading"
            "[contains(@class,'slds-hide_medium') or contains(@class,'slds-show_medium')]"
            "//p[contains(text(),'MAP')]/following-sibling::b2b_buyer_product_details-field-display"
            "//b2b_buyer_pricing-formatted-price"
            ")[last()]"
        )
        map_element = WebDriverWait(driver, WAIT_TIME).until(
            EC.visibility_of_element_located((By.XPATH, map_xpath))
        )
        map_price = map_element.text  # e.g. "$2,039.99"
    except:
        map_price = None
        print(f"[{product}] Could not locate the MAP price.")

    # --------------------------------------------------------------------------
    # 6e. Grab WSP
    # --------------------------------------------------------------------------
    try:
        wsp_xpath = (
            "//td[contains(text(),'WSP')]"
            "/following-sibling::td"
            "//b2b_buyer_pricing-formatted-price"
        )
        wsp_element = WebDriverWait(driver, WAIT_TIME).until(
            EC.visibility_of_element_located((By.XPATH, wsp_xpath))
        )
        wsp_price = wsp_element.text  # e.g. "$1,331.55"
    except:
        wsp_price = None
        print(f"[{product}] Could not locate the WSP price.")

    # --------------------------------------------------------------------------
    # 6f. Append row to our data
    # --------------------------------------------------------------------------
    rows.append([product, map_price, wsp_price])


# ------------------------------------------------------------------------------
# 7. Build final DataFrame
# ------------------------------------------------------------------------------
df = pd.DataFrame(rows, columns=["Variant SKU", "Variant Price", "Cost per item"])

# Convert MAP/WSP to floats (ignore errors if blank/None)
df["Variant Price"] = df["Variant Price"].str.replace(r"[$,]", "", regex=True).astype(float, errors="ignore")
df["Cost per item"] = df["Cost per item"].str.replace(r"[$,]", "", regex=True).astype(float, errors="ignore")

# ------------------------------------------------------------------------------
# 8. Save results and report
# ------------------------------------------------------------------------------
df.to_csv(output_file, index=False)
driver.quit()

print("\n==== Scrape Complete ====")
print(f"Total products: {len(product_list)}")
print(f"Products not fully found (no clickable link): {len(products_not_found_list)}")
if products_not_found_list:
    print("List of not-found products:", products_not_found_list)
print(f"Results saved to {output_file}")