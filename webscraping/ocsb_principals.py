import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_principal_info(url):
    """
    Given a URL to an OCSB school website, fetch the page and
    parse out the Principal's name and email address.
    Return (principal_name, principal_email).
    If not found, return (None, None) or the parts that are found.
    """
    try:
        response = requests.get(url + "/contact", timeout=10)
        response.raise_for_status()  # Raise an HTTPError if the response was an error
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Attempt to locate an element whose text contains "Principal:" but NOT "Vice Principal".
    #    Often, the text "Principal:" might be in a <span>, <p>, or other tag. We'll do a flexible search.
    principal_label = soup.find(
        lambda tag: (
            tag.string and 
            "Principal:" in tag.string and 
            "Vice Principal" not in tag.string
        )
    )
    
    if not principal_label:
        # Could not find the text "Principal:" in the page
        return None, None
    
    # 2. Once we have the label for "Principal:", the principal's name is often in the next <a> tag,
    #    or possibly the next sibling that contains a mailto link. We'll search the next anchor.
    principal_anchor = principal_label.find_next('a', href=True)
    
    # Initialize outputs
    principal_name = None
    principal_email = None
    
    if principal_anchor:
        # The anchor text typically has the name
        principal_name = principal_anchor.get_text(strip=True)
        
        # The anchor's href might be "mailto:someone@ocsb.ca"
        if principal_anchor['href'].lower().startswith('mailto:'):
            principal_email = principal_anchor['href'].split(':', 1)[-1]
    
    return principal_name, principal_email


def main():
    # Load the CSV file into a DataFrame
    df = pd.read_csv('ocsb_schools.csv')
    
    # Add columns for the Principal's name and email if they don't already exist
    if 'PrincipalName' not in df.columns:
        df['PrincipalName'] = None
    if 'PrincipalEmail' not in df.columns:
        df['PrincipalEmail'] = None
    
    # Iterate over each row, retrieve principal info
    for index, row in df.iterrows():
        website = row.get('Website', None)
        
        if not website or not isinstance(website, str):
            print(f"Row {index} does not have a valid 'Website' URL.")
            continue
        
        principal_name, principal_email = get_principal_info(website)
        
        # Store results back into the dataframe
        df.at[index, 'PrincipalName'] = principal_name
        df.at[index, 'PrincipalEmail'] = principal_email
    
    # Save or print the updated DataFrame
    print(df)
    # Optionally, save to a new CSV
    df.to_csv('ocsb_schools_with_principals.csv', index=False)


if __name__ == "__main__":
    main()