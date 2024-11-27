
# Products

The `products` directory contains various scripts, datasets, and templates for managing product data across the platforms Shopify and Reverb. This directory facilitates tasks such as filtering, merging, updating, and exporting product listings.

---

## Files Overview

### 1. IXO22_products.csv
A CSV file containing product details for the Steinberg IXO22 USB-C Audio Interface. This file is used as input in scripts such as `shopify_variants.ipynb` to demonstrate combining individual product listings into a single product with variants.

---

### 2. all-you-need-music-listings-export.csv
This file contains product listings exported from Shopify or other e-commerce platforms. It serves as an input for scripts such as `update_reverb_listings.ipynb`.

---

### 3. aynm_reverb_listings.csv
A CSV file with product listings specifically formatted for the Reverb platform. This file is used in the `reverb_filter_listings.ipynb` script for filtering and exporting products.

---

### 4. disable_product.ipynb
A script for marking Shopify products as inactive.

**Key Features:**
- Appends "Unavailable - " to product titles.
- Adds a custom HTML message in the description indicating the product is no longer available.
- Clears tags and sets inventory policy to deny further purchases.
- Saves the updated product details to a new CSV file.

**Usage:**
- Update the `product_list` variable to point to the input CSV file.
- Run the script to generate an updated CSV file with disabled products.

---

### 5. reverb_filter_listings.ipynb
A script to filter product listings for the Reverb platform based on specific criteria.

**Key Features:**
- Filters listings based on state (e.g., `live`, `sold_out`, `ended`) and price thresholds.
- Saves the filtered product listings to a new CSV file.

**Usage:**
- Update the input file path to point to `aynm_reverb_listings.csv`.
- Run the script to generate `filtered_aynm_reverb_listings.csv`.

---

### 6. shopify_inventory.csv
A CSV file containing inventory data from Shopify. This file is used in `update_reverb_listings.ipynb` to update inventory details on the Reverb platform.

---

### 7. shopify_variants.ipynb
A script for combining individual products into a single product with variants in Shopify.

**Key Features:**
- Merges product data from multiple input files into a single file.
- Sets product options (e.g., color variants).
- Updates titles, handles, and image metadata for consistency across variants.

**Usage:**
- Provide the `variants_file` and `product_file` paths for input.
- Run the script to output a combined product file, such as `IXO22_products_output.csv`.

---

### 8. shopify_variants_template.csv
A template file for defining Shopify product variants. It serves as a base for the `shopify_variants.ipynb` script.

---

### 9. update_reverb_listings.ipynb
A script to synchronize inventory data between Shopify and Reverb.

**Key Features:**
- Matches SKUs between Shopify and Reverb listings.
- Updates inventory quantities on Reverb based on Shopify's data.
- Saves the updated Reverb listings to a new CSV file.

**Usage:**
- Provide paths for the input files (`reverb_listings_csv` and `shopify_inventory_csv`).
- Run the script to generate `reverb_listings_updated.csv`.

---

## General Workflow

1. **Prepare Input Files:**
   Ensure the relevant CSV files (e.g., product listings, inventory data) are present and correctly formatted.

2. **Run Scripts:**
   Execute the desired Jupyter Notebooks or Python scripts for filtering, merging, or updating product data.

3. **Export Results:**
   The output files are saved in CSV format, ready for use in Shopify, Reverb, or other platforms.

---

## Notes

- The scripts are tailored for specific use cases and platforms. Modifications may be necessary for other datasets or requirements.
- Ensure that CSV headers match the expected format for the scripts to work correctly.
- Use responsibly and comply with the terms and conditions of the platforms.

## License

This project is licensed under the MIT License.
