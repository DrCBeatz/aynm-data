
# Customer Data Processing for Draw Submissions

This repository provides scripts for processing handwritten customer data collected via physical draw cards, using Microsoft Azure Cognitive Services for OCR. The workflow involves scanning cards for customer name, email, and phone number, cleaning the OCR output, and formatting it into a CSV for Shopify to add customers to the mailing list.

## Files

- `customer_csv.ipynb`: Converts the final CSV into a Shopify-compatible format for importing customer data.
- `draw.py`: Contains a list of image filenames to process for OCR.
- `init_handprint.sh`: Initializes the `handprint` tool with Microsoft Azure credentials.
- `myazurecredentials.json`: Stores Azure Vision API credentials (subscription key and endpoint).
- `name_script.py`: Converts manually cleaned OCR text into a structured CSV file.
- `names_txt.py`: Contains manually cleaned names, emails, and phone numbers in a structured text format.
- `ocr.py`: Performs OCR on each image in `draw.py`, using Azure's Vision API.

## Workflow

### Step 1: Initialize Azure OCR

Use the `init_handprint.sh` script to initialize the `handprint` tool with Microsoft Azure credentials:
```bash
./init_handprint.sh
```
Ensure your credentials are stored in `myazurecredentials.json`.

### Step 2: Run OCR on Images

Run `ocr.py` to perform OCR on each image listed in `draw.py`. This script reads images, processes each using Microsoft Azure's OCR, and outputs the initial data for manual review.

```bash
python ocr.py
```

### Step 3: Manually Clean OCR Output

Review the OCR output and manually edit it into the format in `names_txt.py`, ensuring each entry contains:
- `NAME`: Customer name
- `EMAIL`: Customer email
- `PHONE`: Customer phone number

### Step 4: Convert to CSV Format

Run `name_script.py` to convert the structured text data in `names_txt.py` into a CSV file (`draw.csv`).

```bash
python name_script.py
```

### Step 5: Format for Shopify Import

Use the Jupyter notebook `customer_csv.ipynb` to further process `draw.csv` into a Shopify-compatible CSV (`draw_output.csv`), with columns split for `First Name`, `Last Name`, email preferences, and tags.

## File Details

### `init_handprint.sh`

This shell script authenticates `handprint` with Microsoft Azure for OCR.

### `ocr.py`

Uses the `handprint` tool to perform OCR on each image listed in `draw.py`.

### `name_script.py`

Processes manually cleaned text data into a structured CSV format with columns `Name`, `Email`, and `Phone`.

### `customer_csv.ipynb`

Converts the output of `name_script.py` into a Shopify-compatible CSV format:
- Splits `Name` into `First Name` and `Last Name`.
- Adds email marketing preferences and tags.

## Example

#### Input Format (names_txt.py)

```plaintext
NAME: John Doe
EMAIL: johndoe@example.com
PHONE: 123-456-7890
```

#### Output Format (draw_output.csv)

```csv
First Name,Last Name,Email,Phone,Accepts Email Marketing,Tags
John,Doe,johndoe@example.com,123-456-7890,yes,local
```

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please open an issue or reach out to the repository owner.
