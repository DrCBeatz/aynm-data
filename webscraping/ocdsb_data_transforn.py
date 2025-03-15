import pandas as pd

def parse_address(address_str):
    """
    Naive parser for addresses in the format:
    "Street City, ON PostalCode"
    Returns Address 1, City, Province, Postal Code.
    """
    # Remove extra surrounding quotes/spaces
    address_str = address_str.strip().strip('"')

    address_1 = ""
    city = ""
    province = "Ontario"  # fixed
    postal_code = ""

    # Expected format: "Some Street City, ON K2S 1G8"
    parts = [p.strip() for p in address_str.split(",")]
    if len(parts) >= 2:
        # The first part should be "Street City"
        first_part = parts[0]
        # The second part might be "ON K2S 1G8"
        second_part = parts[1]

        # Split the first part into words; last word is likely the city
        tokens = first_part.split()
        if len(tokens) > 1:
            city = tokens[-1]
            address_1 = " ".join(tokens[:-1])
        else:
            # If there's only one token, treat it as the address
            address_1 = first_part

        # Parse the second part for "ON <postal_code>"
        second_tokens = second_part.split(None, 1)
        if len(second_tokens) > 1:
            # The part after 'ON' should be the postal code
            postal_code = second_tokens[1].strip()
    else:
        # If we can’t split well, just store everything in address_1
        address_1 = address_str

    return address_1, city, province, postal_code

def transform_ocdsb_data(input_csv, output_csv):
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
        # Extract principal's first and last name
        principal_name = str(row['Principal']).strip('"').strip()
        principal_parts = principal_name.split(None, 1)  # split on first space
        first_name = principal_parts[0] if len(principal_parts) > 0 else ""
        last_name = principal_parts[1] if len(principal_parts) > 1 else ""

        # Determine School Email: use Principal_Email if not empty, else use Email
        principal_email = str(row.get('Principal_Email', '')).strip()
        fallback_email = str(row.get('Email', '')).strip()
        school_email = principal_email if principal_email else fallback_email

        # Parse the address
        address_1, city, province, postal_code = parse_address(str(row['Address']))

        transformed_data['School Board'].append('Ottawa-Carleton District School Board')
        transformed_data['School Name'].append(row['School Name'])
        transformed_data['Website URL'].append(row['Website'])
        transformed_data['FIRST'].append(first_name)
        transformed_data['LAST'].append(last_name)
        transformed_data['Contact Title'].append('Principal')
        transformed_data['School Phone'].append(row['Phone'])
        transformed_data['School Email'].append(school_email)
        transformed_data['Address 1'].append(address_1)
        transformed_data['City'].append(city)
        transformed_data['Province'].append(province)
        transformed_data['Postal Code'].append(postal_code)

    # 3. Convert to a pandas DataFrame
    df_transformed = pd.DataFrame(transformed_data)

    # 4. Save to CSV
    df_transformed.to_csv(output_csv, index=False)

if __name__ == "__main__":
    input_csv = "ocdsb_schools_with_principals.csv"
    output_csv = "ocdsb_schools_transformed.csv"
    transform_ocdsb_data(input_csv, output_csv)
    print(f"Transformed data saved to {output_csv}")