
# Webscraping

The `webscraping` directory contains scripts and tools for scraping product information from various music supplier and retailer websites and preparing the data for use in Shopify.

## Files Overview

### 1. coast_webscrape.ipynb
This Jupyter Notebook is designed to scrape product information from the Coast music supplier's B2B website. The script logs into the website, searches for specified product SKUs, extracts relevant details (e.g., vendor, title, price, description, image URL), and saves the results into a CSV file.

**Key Features:**
- Uses Selenium WebDriver for automation.
- Supports headless mode for background execution.
- Extracts detailed product information, including pricing and descriptions.
- Saves results in a CSV format suitable for Shopify.
- Also checks and saves in CSV file whether product is in-stock currently out of stock.

---

### 2. Erikson Music Webscrape.ipynb
This Jupyter Notebook automates the extraction of product details from the Erikson Music supplier's website. The workflow is similar to the Coast Webscrape but customized for Erikson's website structure.

**Key Features:**
- Automates login and navigation.
- Extracts vendor, SKU, price, description, and images.
- Outputs the data in CSV format for Shopify compatibility.

---

### 3. image_download.py
A standalone Python script to automatically download product images for webscraped products (e.g. using other webscraping scripts in this directory) based on a CSV file containing `Variant SKU` and `Product Image` fields.

**Key Features:**
- Reads input from a CSV file.
- Downloads images from URLs specified in the `Product Image` column.
- Saves images locally with filenames based on the `Variant SKU`.

**Usage:**
1. Update the `INPUT_FILE` constant to point to the input CSV file.
2. Run the script to download images.

---

### 4. Long & McQuade Webscrape.ipynb
This notebook is tailored for scraping product data from the Long & McQuade website.

**Key Features:**
- Automates the search and extraction of product details.
- Retrieves pricing, brand, title, descriptions, and image URLs.
- Saves extracted data in a Shopify-compatible CSV format.

---

## Prerequisites

1. **Python Libraries:**
   - `selenium`
   - `pandas`
   - `requests`

2. **ChromeDriver:**
   Ensure that the correct version of ChromeDriver is installed and its path is set in the scripts.

3. **Environment:**
   - Python 3.7 or later.
   - Web browser (Chrome recommended).
   - Jupyter Notebook for `.ipynb` files.

---

## General Usage

1. **Setup Credentials:**
   Update the `username` and `password` variables in the webscrape scripts to provide login details for the respective supplier websites.

2. **Specify Product SKUs:**
   Modify the `product_list` array or provide an input CSV file with product SKUs.

3. **Run the Script:**
   - Execute the Jupyter Notebook or Python script in the desired environment.
   - Ensure the website URLs and configurations (e.g., selectors) are up-to-date.

4. **Output:**
   The results are saved as CSV files in the same directory.

---

## Notes

- These scripts are configured for specific websites and may require updates if the website structure changes.
- Use responsibly and comply with the terms of service of the supplier websites.
- Add appropriate headers and delays (`WAIT_TIME`) to avoid being blocked.

## License

This project is licensed under the MIT License.

