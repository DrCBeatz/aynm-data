import pandas as pd

def filter_discontinued_products(input_file, output_file):
    # Load the CSV file into a DataFrame. Using dtype=str ensures that all columns
    # are read as strings, preserving any special characters like asterisks.
    df = pd.read_csv(input_file, dtype=str)

    # Filter rows to keep only those with an asterisk in the 'Variant SKU' column.
    # .str.contains() looks for a pattern in each string.
    # The escape sequence '\*' ensures we treat the asterisk literally.
    filtered_df = df[df['Variant SKU'].str.contains('\*', na=False)]

    # Save the filtered DataFrame to a new CSV file (without the index).
    # By default, all columns are included in the CSV output.
    filtered_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    # Example usage:
    filter_discontinued_products(
        input_file="discontinued_products.csv", 
        output_file="discontinued_products_filtered.csv"
    )