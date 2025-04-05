import pandas as pd

def update_cost_per_item():
    # 1) Read CSV files into DataFrames.
    #    Use dtype=str for columns that you want to preserve exactly (no leading zeros dropped, etc.)
    df = pd.read_csv(
        'evans_products.csv',
        dtype={
            'Variant SKU': str,           # ensure SKU remains as string
            'Variant Barcode': str        # ensure Barcode remains as string (if present)
        }
    )
    
    df_daddario = pd.read_csv(
        'daddario_pricelist_2025.csv',
        dtype={'ProdCode': str}  # ensure product codes remain as string
    )
    
    # 2) Create a dictionary mapping from ProdCode -> Net Price
    price_map = dict(zip(df_daddario['ProdCode'], df_daddario['Net Price']))
    
    # 3) Store the old cost per item to compare later.
    old_cost_series = df['Cost per item'].copy()
    
    # 4) Compute the new cost where there's a match, otherwise NaN.
    matched_price_series = df['Variant SKU'].map(price_map)
    
    # 5) Identify which rows will actually change.
    #    Updated means: (a) there's a match (not NaN), and (b) the new cost differs from the old cost.
    will_update_mask = matched_price_series.notna() & (matched_price_series != old_cost_series)
    
    # 6) Apply the updates: replace old cost with the matched price where available, otherwise keep old cost.
    df['Cost per item'] = matched_price_series.fillna(old_cost_series)
    
    # 7) Extract the SKUs that were updated.
    updated_skus = df.loc[will_update_mask, 'Variant SKU'].tolist()
    
    # 8) Print information about updated products.
    print(f"Number of products updated: {len(updated_skus)}")
    if updated_skus:
        print("SKUs of updated products:")
        for sku in updated_skus:
            print(f" - {sku}")
    else:
        print("No products were updated.")
    
    # 9) Save the updated DataFrame to a new CSV file.
    df.to_csv('evans_products_updated.csv', index=False)

if __name__ == "__main__":
    update_cost_per_item()

