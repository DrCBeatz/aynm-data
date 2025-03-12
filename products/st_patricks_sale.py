import pandas as pd

# Read the CSV file, ensuring 'Variant SKU' and 'Variant Barcode' remain strings
df = pd.read_csv(
    'st_patricks_products.csv',
    dtype={
        "Variant SKU": str,
        "Variant Barcode": str
    }
)

# Helper function to add "on-sale" to the Tags column
def add_onsale(tags_cell):
    # If the cell is NaN or empty, just return "on-sale"
    if pd.isna(tags_cell) or not tags_cell.strip():
        return "on-sale"
    
    # Split tags by comma, strip whitespace, and filter out empty strings
    tags_list = [tag.strip() for tag in tags_cell.split(',') if tag.strip()]
    
    # Append "on-sale" if it's not already present
    if "on-sale" not in tags_list:
        tags_list.append("on-sale")
    
    # Return the comma-separated tags
    return ",".join(tags_list)

# 1. Add "on-sale" to the Tags column
df['Tags'] = df['Tags'].apply(add_onsale)

# 2. Change all fields in 'Type' to 'Clearance'
df['Type'] = 'Clearance'

# 3. Move 'Variant Price' to 'Variant Compare At Price'
df['Variant Compare At Price'] = df['Variant Price']

# 4. Discount 'Variant Price' by 15% (i.e., multiply by 0.85)
#    Make sure 'Variant Price' is numeric. If it's not, you may need to convert it first.
df['Variant Price'] = pd.to_numeric(df['Variant Price'], errors='coerce') * 0.85

# (Optional) Save to a new CSV, preserving the string types for 'Variant SKU' and 'Variant Barcode'
df.to_csv("st_patricks_products_updated.csv", index=False)