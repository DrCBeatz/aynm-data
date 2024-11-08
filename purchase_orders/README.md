# Stocky to Coast PO Conversion

This directory contains a Jupyter notebook script (`stocky_to_coast_po.ipynb`) that converts a purchase order CSV file from Stocky into a format compatible with the Coast B2B shopping cart. This conversion process also works for both Erikson Music & Erikson Audio orders.

## Files

- `coast_cart.csv`: Template CSV file for Coast cart format.
- `stocky_to_coast_po.ipynb`: Jupyter notebook script that performs the conversion.

## Prerequisites

- **Python 3.6+**
- **pandas**: For handling CSV file operations.
- **numpy**: For numerical operations.

To install dependencies, use:
```bash
pip install pandas numpy
```

## Usage

1. Place your Stocky purchase order file (e.g., `po_1848.csv`) in the working directory.
2. Open the `stocky_to_coast_po.ipynb` notebook and run the cells.
3. The output CSV file will be generated as `new_coast_cart_<PO_NUMBER>.csv` (e.g., `new_coast_cart_1848.csv`).

### CSV Field Mapping

The script maps fields from Stocky’s CSV file to Coast’s format as follows:

- **Stocky `SKU`** → Coast `Item Id`
- **Stocky `Qty Ordered`** → Coast `Qty Ordered`
- **Stocky `Cost (base)`** → Coast `Unit Price`
- **Stocky `Total Cost (base)`** → Coast `Extended Price`

### Example Input File (`po_1848.csv`)

```csv
SKU,Qty Ordered,Cost (base),Total Cost (base)
ABC123,10,15.00,150.00
DEF456,5,20.00,100.00
```

### Example Output File (`new_coast_cart_1848.csv`)

```csv
Item Id,Qty Ordered,Unit Price,Extended Price
ABC123,10,15.00,150.00
DEF456,5,20.00,100.00
```

## Notes

Ensure the Stocky CSV file matches the expected structure with columns for SKU, Qty Ordered, Cost (base), and Total Cost (base).

## License

This project is licensed under the MIT License.
