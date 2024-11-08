# Label creation script for creating printed labels with scannable barcodes.

This directory includes a script, `create-label.py`, that generates label files for P-touch editor v5.4+ software (for the Brother QL-570 Label Printer), based on product data from a CSV file exported from Shopify. It updates XML templates with product details, creates labels, and compresses files for easy distribution.

## Directory Structure

The `labels` directory includes the following files:

- `Object0.bmp`: An image file of the AYNM logo in the label.
- `compress.py`: A script to compress the label files.
- `create-label.py`: The main script to generate the label.
- `label.xml`: The primary label file, created from a template.
- `prop.xml`: Property file containing metadata for the label.
- `template_reg.xml`: Template XML file for regular price labels.
- `template_sale.xml`: Template XML file for sale price labels.

## Getting Started

### Prerequisites

- **Python** (version 3.6+)
- **pandas**: For processing CSV files.
  
To install dependencies, run:
```bash
pip install pandas
```

## Usage
To run the `create-label.py` script, navigate to the directory where it is located and execute:

```bash
python create-label.py -f <CSV_FILE>
```
- -f, --file: Path to the CSV file (default: `products_export.csv`).

## CSV File Format
The CSV file should contain the following columns:

- **Title:** Product name.
- **Variant SKU:** SKU of the product variant.
- **Variant Barcode:** Barcode for the product.
- **Variant Price:** Price of the product variant.
- **Variant Compare At Price:** (Optional) Regular price for comparison in case of a sale.
- **Vendor:** Vendor name.

### Example
```csv
Title,Variant SKU,Variant Barcode,Variant Price,Variant Compare At Price,Vendor
"Product A","SKU123","123456789012","19.99","24.99","VendorA"
```

## Script Details
The script performs the following steps:

1. **Copy the Template File**: Based on the `sale` variable, either `template_sale.xml` or `template_reg.xml` is used as a base for the label.
2. **Parse the CSV**: Reads the CSV file specified with product details.
3. **Replace Placeholders**: Updates placeholders in the template with actual values from the CSV.
- `[SKU]`: Replaced by the product SKU.
- `[VENDOR]`: Replaced by the vendor's name.
- `[TITLE]`: The product title is wrapped to fit on the label.
- `[reg-pr]`: The regular price.
- `[sale-pr]`: The sale price (if applicable).
4. **Compress Files**: Uses `compress.py` to package the files into a ZIP file, `my_label.lbx`.
   
### Compression
The `compress.py` script compresses `label.xml`, `prop.xml`, and `Object0.bmp` into a `.lbx` file.

### Utilities
- **replace.py**: Contains helper functions for string replacements.
 - `nth_repl_all()`: Replaces the nth occurrence of a substring.
- `replace_file_text()`: Replaces a specified string in label.xml.

## License
This project is licensed under the MIT License.
