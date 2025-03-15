import pandas as pd
import re

def parse_address(address_str):
    """
    Attempts to parse the school address into:
      Address 1, City, and Postal Code.
    This is a simplified approach, as real-world addresses can vary greatly.
    """
    # Province is always 'Ontario' (per instructions).
    # We'll look for a pattern containing the province, if present.
    province = "Ontario"
    # Initialize default returns
    address_1 = ""
    city = ""
    postal_code = ""

    # If the string contains 'Ontario', assume format like:
    # "5115 Kanata Avenue, Kanata, Ontario K2K 3K5"
    if 'Ontario' in address_str:
        # Split by commas first
        parts = [p.strip() for p in address_str.split(',')]
        if len(parts) >= 3:
            address_1 = parts[0]
            city = parts[1]
            # The last part should contain "Ontario K2K 3K5" (or similar)
            # Extract the postal code by removing 'Ontario'
            remainder = parts[2].replace("Ontario", "").strip()
            postal_code = remainder
        else:
            # Fallback if not exactly 3 parts
            address_1 = address_str
    else:
        # Otherwise, try a simplified approach for addresses without "Ontario", 
        # e.g. "236 Lévis Avenue Vanier K1L 6H8"
        # We'll look for a Canadian postal code pattern near the end:
        # something like 'K1L 6H8' or 'K1L6H8'
        match = re.search(r'([A-Z]\d[A-Z]\s?\d[A-Z]\d)$', address_str, re.IGNORECASE)
        if match:
            postal_code = match.group(1)
            # remove that from the address, then the last 'word' might be the city
            address_str = address_str.replace(postal_code, '').strip()

            # Heuristic: the city is often the final 'token' after removing postal code
            # For example: "236 Lévis Avenue Vanier"
            # We'll split on spaces and take the last chunk as city:
            tokens = address_str.split()
            if len(tokens) > 1:
                city = tokens[-1]
                address_1 = ' '.join(tokens[:-1])
            else:
                address_1 = address_str
        else:
            # If we can't parse well, just assume everything is address_1
            address_1 = address_str

    return address_1.strip(), city.strip(), province, postal_code.strip()

def transform_ocsb_data(input_csv, output_csv):
    # 1. Load the CSV
    df = pd.read_csv(input_csv)

    # 2. Build a new DataFrame with the requested columns
    transformed_data = {
        'School Board': [],
        'School Name': [],
        'Website URL': [],
        'FIRST': [],
        'LAST': [],
        'Contact Title': [],
        'School Phone': [],
        'School Email': [],
        'Address 1': [],
        'City': [],
        'Province': [],
        'Postal Code': []
    }

    for _, row in df.iterrows():
        # Extract principal's first and last name (naive split on first space)
        principal_name = str(row['Principal']).strip()
        principal_parts = principal_name.split(None, 1)  # split on first space
        first_name = principal_parts[0] if len(principal_parts) > 0 else ""
        last_name = principal_parts[1] if len(principal_parts) > 1 else ""

        # Parse the address
        address_1, city, province, postal_code = parse_address(str(row['School_Address']))

        transformed_data['School Board'].append('Ottawa Catholic School Board')
        transformed_data['School Name'].append(row['School Name'])
        transformed_data['Website URL'].append(row['Website'])
        transformed_data['FIRST'].append(first_name)
        transformed_data['LAST'].append(last_name)
        transformed_data['Contact Title'].append('Principal')
        transformed_data['School Phone'].append(row['Phone'])
        transformed_data['School Email'].append(row['Principal Email'])
        transformed_data['Address 1'].append(address_1)
        transformed_data['City'].append(city)
        transformed_data['Province'].append(province)
        transformed_data['Postal Code'].append(postal_code)

    # 3. Convert to a pandas DataFrame
    df_transformed = pd.DataFrame(transformed_data)

    # 4. Save to CSV
    df_transformed.to_csv(output_csv, index=False)

if __name__ == "__main__":
    input_csv = "ocsb_schools_with_principals.csv"
    output_csv = "ocsb_schools_transformed.csv"
    transform_ocsb_data(input_csv, output_csv)
    print(f"Transformed data saved to {output_csv}")