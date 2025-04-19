#!/usr/bin/env python3
"""
Update prices in profile_products_combined.csv from profile_price_list.csv.

• 'Cost per item'  <-  'Dealer Price'
• 'Variant Price'  <-  'MAP'   (only if MAP is non‑blank)

Matching key:
    product_df['Variant SKU']  ==  price_df['Model']

The script leaves 'Variant SKU' and 'Variant Barcode' untouched (dtype string),
prints a summary of how many rows were updated, and saves the result to
profile_products_combined_updated.csv.
"""

import pandas as pd
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration – edit filenames here if yours differ
PRODUCT_FILE = "profile_products_combined.csv"
PRICE_FILE   = "profile_price_list.csv"
OUTPUT_FILE  = "profile_products_combined_updated.csv"
# ----------------------------------------------------------------------

def main() -> None:
    cwd = Path.cwd()

    # --- 1) Load both CSVs ---------------------------------------------------
    df_prod = pd.read_csv(
        cwd / PRODUCT_FILE,
        dtype={          # preserves formatting in these ID columns
            "Variant SKU": "string",
            "Variant Barcode": "string",
        },
        keep_default_na=False   # keep empty cells truly empty
    )

    df_price = pd.read_csv(
        cwd / PRICE_FILE,
        dtype={"Model": "string"},   # ensure key column is string, too
        keep_default_na=False
    )

    # --- 2) Build a quick lookup from SKU -> (Dealer Price, MAP) ------------
    price_lookup = (
        df_price
        .set_index("Model")[["Dealer Price", "MAP"]]
        .to_dict(orient="index")
    )

    # --- 3) Iterate once, apply updates, keep track --------------------------
    updated_skus = []

    def apply_updates(row):
        sku = row["Variant SKU"]
        if sku in price_lookup:
            dealer_price = price_lookup[sku]["Dealer Price"]
            map_price    = price_lookup[sku]["MAP"]

            changed = False
            # Update Cost per item
            if dealer_price != "":
                row["Cost per item"] = dealer_price
                changed = True
            # Update Variant Price if MAP present
            if map_price != "":
                row["Variant Price"] = map_price
                changed = True

            if changed:
                updated_skus.append(sku)
        return row

    df_prod = df_prod.apply(apply_updates, axis=1)

    # --- 4) Save the updated dataframe --------------------------------------
    df_prod.to_csv(cwd / OUTPUT_FILE, index=False)

    # --- 5) Report -----------------------------------------------------------
    print(f"Finished.\nUpdated {len(updated_skus)} product(s).")
    if updated_skus:
        print("SKUs updated:")
        for sku in updated_skus:
            print(" •", sku)
    print(f"Result written to {OUTPUT_FILE}")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()