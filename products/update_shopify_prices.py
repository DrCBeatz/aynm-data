# update_shopify_prices.py

import pandas as pd
import numpy as np

def update_shopify_prices(
    products_file="yamaha_products3.csv",
    prices_file="yamaha_products3_output.csv",
    output_file="yamaha_products3_updated.csv"
):
    """
    Loads two CSV files: 
      - One with the Shopify products ("products_file")
      - One with the updated prices ("prices_file")
    Matches on 'Variant SKU' and updates 'Variant Price' and/or 'Cost per item'
    in the Shopify file based on the corresponding non-null, non-zero values 
    from the prices file. Writes the result to 'output_file'.

    This version ensures that 'Variant SKU' and 'Variant Barcode' columns 
    remain as strings (so no leading zeros or formatting changes occur),
    and it also tracks the rows that have been modified:
      - The number of modified rows
      - The specific SKUs of modified rows
    """
    
    # Columns we want to preserve as strings (to avoid losing leading zeros etc.)
    preserve_as_str_cols = ["Variant SKU", "Variant Barcode"]
    
    # Step 1: Read the products CSV and the prices CSV, forcing columns to be strings
    df_products = pd.read_csv(products_file, dtype=str)
    df_prices = pd.read_csv(prices_file, dtype=str)
    
    # Ensure 'Variant SKU'/'Variant Barcode' columns exist, even if empty
    for col in preserve_as_str_cols:
        if col not in df_products.columns:
            df_products[col] = ""
        if col not in df_prices.columns:
            df_prices[col] = ""
    
    # Columns we will treat as numeric for comparison
    numeric_cols = ["Variant Price", "Cost per item"]
    
    # Convert numeric columns in both DataFrames to float for comparison
    for col in numeric_cols:
        if col in df_products.columns:
            df_products[col] = pd.to_numeric(df_products[col], errors="coerce")
        if col in df_prices.columns:
            df_prices[col] = pd.to_numeric(df_prices[col], errors="coerce")
    
    # Step 2: Merge DataFrames on 'Variant SKU' (left join to keep all product rows)
    # suffixes=("", "_new") so df_prices columns appear as e.g., 'Variant Price_new'
    merge_cols = ["Variant SKU"] + numeric_cols
    df_merged = df_products.merge(
        df_prices[merge_cols], 
        on="Variant SKU",
        how="left",
        suffixes=("", "_new")
    )
    
    # Before updating, let's keep track of the old values for comparison
    df_merged["Old_Variant_Price"] = df_merged["Variant Price"]
    df_merged["Old_Cost_per_Item"] = df_merged["Cost per item"]
    
    # Step 3: Update numeric columns
    # We only update if:
    #  - The new value is not NaN
    #  - The new value is not zero
    #  - The old value is different from the new value
    
    if "Variant Price_new" in df_merged.columns:
        df_merged["Variant Price"] = np.where(
            (df_merged["Variant Price_new"].notna()) &
            (df_merged["Variant Price_new"] != 0) &
            (df_merged["Variant Price"] != df_merged["Variant Price_new"]),
            df_merged["Variant Price_new"],
            df_merged["Variant Price"]
        )
        
    if "Cost per item_new" in df_merged.columns:
        df_merged["Cost per item"] = np.where(
            (df_merged["Cost per item_new"].notna()) &
            (df_merged["Cost per item_new"] != 0) &
            (df_merged["Cost per item"] != df_merged["Cost per item_new"]),
            df_merged["Cost per item_new"],
            df_merged["Cost per item"]
        )
    
    # Step 4: Identify which rows actually changed in "Variant Price" or "Cost per item"
    # We'll compare the new values with the old values
    price_changed = df_merged["Variant Price"] != df_merged["Old_Variant_Price"]
    cost_changed  = df_merged["Cost per item"] != df_merged["Old_Cost_per_Item"]
    
    # A row is considered changed if either price_changed or cost_changed is True
    changed_rows = price_changed | cost_changed
    
    # Collect the SKUs of changed rows
    updated_skus = df_merged.loc[changed_rows, "Variant SKU"].tolist()
    
    # Count how many unique rows were updated
    num_rows_modified = len(updated_skus)
    
    # Step 5: Cleanup temporary columns
    # Drop the columns we no longer need: _new columns and Old_* columns
    cols_to_drop = []
    if "Variant Price_new" in df_merged.columns:
        cols_to_drop.append("Variant Price_new")
    if "Cost per item_new" in df_merged.columns:
        cols_to_drop.append("Cost per item_new")
    cols_to_drop += ["Old_Variant_Price", "Old_Cost_per_Item"]
    
    df_merged.drop(columns=cols_to_drop, inplace=True)
    
    # Step 6: Save the final DataFrame as CSV
    df_merged.to_csv(output_file, index=False)
    
    # Finally, report on the number of modified rows and their SKUs
    print(f"Number of rows modified: {num_rows_modified}")
    if num_rows_modified > 0:
        print("Updated SKUs:")
        for sku in updated_skus:
            print("  -", sku)

if __name__ == "__main__":
    # Example usage
    update_shopify_prices(
        products_file="yamaha_products1.csv",
        prices_file="yamaha_products1_output.csv",
        output_file="yamaha_products1_updated.csv"
    )