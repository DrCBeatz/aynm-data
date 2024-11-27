
# aynm-data Repository

This repository contains scripts, datasets, and tools for managing data related to All You Need Music (AYNM). It supports operations such as web scraping, product management, customer data processing, and purchase order conversion.

---

## Directory Overview

### 1. `customers`
Scripts for processing handwritten customer data collected via physical draw cards. It includes OCR tools and workflows to convert scanned data into Shopify-compatible CSV files.

**Highlights:**
- Uses Microsoft Azure Cognitive Services for OCR.
- Includes scripts to format customer data for Shopify imports.

**Key Files:**
- `customer_csv.ipynb`: Converts OCR data into Shopify-compatible CSV.
- `ocr.py`: Performs OCR on draw card images.

For detailed documentation, see the [README.md](customers/README.md) in the `customers` directory.

---

### 2. `labels`
Tools for creating and printing product labels with scannable barcodes. It generates labels based on product data exported from Shopify.

**Highlights:**
- Creates label files for P-touch Editor software.
- Supports sale and regular price labels.

**Key Files:**
- `create-label.py`: Generates labels using XML templates.
- `compress.py`: Packages label files into a compressed format.

For detailed documentation, see the [README.md](labels/README.md) in the `labels` directory.

---

### 3. `products`
Scripts and datasets for managing product data across multiple platforms, such as Shopify and Reverb. It includes tools for filtering, merging, and updating product listings.

**Highlights:**
- Combines individual products into a single product with variants.
- Synchronizes inventory data between Shopify and Reverb.

**Key Files:**
- `shopify_variants.ipynb`: Combines products into variants.
- `update_reverb_listings.ipynb`: Updates Reverb listings based on Shopify inventory.

For detailed documentation, see the [README.md](products/README.md) in the `products` directory.

---

### 4. `purchase_orders`
Scripts for converting Stocky purchase orders into formats compatible with Coast, Erikson Music, and Erikson Audio shopping carts.

**Highlights:**
- Maps fields between Stocky and Coast formats.
- Supports bulk purchase order processing.

**Key Files:**
- `stocky_to_coast_po.ipynb`: Converts Stocky purchase orders to Coast-compatible CSV files.

For detailed documentation, see the [README.md](purchase_orders/README.md) in the `purchase_orders` directory.

---

### 5. `webscraping`
Scripts for scraping product data from supplier websites (e.g., Coast, Erikson Music) and preparing it for Shopify import.

**Highlights:**
- Automates login, search, and data extraction.
- Downloads product images.

**Key Files:**
- `Coast Webscrape.ipynb`: Scrapes data from Coast B2B.
- `image_download.py`: Downloads product images.

For detailed documentation, see the [README.md](webscraping/README.md) in the `webscraping` directory.

---

## Repository Structure

```
aynm-data/
├── customers/
├── labels/
├── products/
├── purchase_orders/
├── webscraping/
├── .gitattributes
├── README.md
```

---

## Prerequisites

- **Python 3.6+**
- Required Python libraries: `pandas`, `numpy`, `requests`, `selenium`
- For specific dependencies, refer to the README files in each directory.

---

## Usage

1. Explore the directories for scripts tailored to your use case.
2. Follow the workflows outlined in the respective README files.
3. Run the scripts or Jupyter notebooks as needed.

---

## Notes

- Ensure all required dependencies are installed before running scripts.
- Use responsibly and comply with the terms and conditions of external services.

---

## License

This project is licensed under the MIT License.
