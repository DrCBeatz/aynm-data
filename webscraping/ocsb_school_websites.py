import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

def extract_school_info_block(soup):
    """
    Find the lines of text after we see 'SCHOOL INFORMATION' in the page,
    and collect them until we hit 'ACCESSIBILITY' or run out of lines.
    Returns a string with those lines joined by newlines.
    """
    all_text = soup.get_text(separator='\n')
    lines = [line.strip() for line in all_text.split('\n') if line.strip()]

    # Find index of "SCHOOL INFORMATION"
    start_index = None
    for i, line in enumerate(lines):
        if "SCHOOL INFORMATION" in line.upper():
            start_index = i
            break

    if start_index is None:
        return None  # not found

    # Collect lines after "SCHOOL INFORMATION," stopping if we see "ACCESSIBILITY"
    info_lines = []
    for j in range(start_index, len(lines)):
        if "ACCESSIBILITY" in lines[j].upper():
            break
        info_lines.append(lines[j])

    return "\n".join(info_lines)

def parse_info_block(info_block):
    """
    From the collected lines after 'SCHOOL INFORMATION', extract:
      - phone (by searching lines for 'Phone:')
      - a school-level email (by searching lines for 'Email:')
      - an address line (heuristic: line with a postal code or city naming)
    Returns (phone, school_email, address)
    """
    phone, school_email, address = None, None, None

    # 1) Try to find phone in lines with "Phone:"
    phone_match = re.search(r'(?i)phone:\s?([\(\)\d\s\-\.xext]+)', info_block)
    if phone_match:
        # e.g. '613-746-4822'
        raw_phone = phone_match.group(1).strip()
        # Clean up phone
        phone = re.sub(r'[^\d\-\.\(\)\sxext]', '', raw_phone)

    # 2) Try to find an email in lines with "Email:"
    email_match = re.search(r'(?i)email:\s?([\w.\-+]+@[\w.\-]+\.\w+)', info_block)
    if email_match:
        school_email = email_match.group(1).strip()

    # 3) Heuristic for address: lines containing a typical postal code or city
    # e.g. '5115 Kanata Avenue, Kanata, ON K2K 3K5'
    # We'll just look for a Canadian postal code: K1L, K2K, etc.
    # or you can adapt for other city/region searches
    lines = info_block.split('\n')
    for line in lines:
        # Simple check for something like 'K\d[A-Za-z] \d[A-Za-z]\d'
        if re.search(r'(?i)\bK\d[A-Za-z]\s?\d[A-Za-z]\d\b', line):
            address = line.strip()
            break

    return phone, school_email, address

def find_principal_tags(soup):
    """
    Returns all tags whose text contains 'Principal' or 'Acting Principal'
    """
    principal_tags = soup.find_all(
        lambda t: t.name in ['p','span','div','small','li'] 
                  and re.search(r'(Principal|Acting Principal)', t.get_text(), re.IGNORECASE)
    )
    return principal_tags

def parse_principal_info(tag):
    """
    Given a single BeautifulSoup tag that includes something like
    'Principal: John Smith <a href="mailto:john.smith@ocsb.ca">john.smith@ocsb.ca</a>'

    Returns (principal_name, principal_email)
    """
    snippet_text = tag.get_text(separator=' ', strip=True)
    principal_name, principal_email = None, None

    # Check for an anchor with mailto:
    anchor = tag.find('a', href=re.compile(r'mailto:', re.IGNORECASE))
    if anchor:
        # E.g. mailto:john.smith@ocsb.ca
        principal_email = anchor['href'].replace('mailto:', '').strip()
        link_text = anchor.get_text(strip=True)
        if link_text.lower() != principal_email.lower():
            # If the link text is something like "John Smith"
            principal_name = link_text
        else:
            # Look outside the link
            snippet_no_email = snippet_text.replace(principal_email, '')
            snippet_no_email = re.sub(r'(Principal|Acting Principal)\W*', '',
                                      snippet_no_email, flags=re.IGNORECASE)
            principal_name = snippet_no_email.strip()
    else:
        # If there's no anchor, try to find an email in the text
        email_match = re.search(r'[\w.\-+]+@[\w.\-]+\.\w+', snippet_text)
        if email_match:
            principal_email = email_match.group(0)
            snippet_text = snippet_text.replace(principal_email, '')

        # Remove 'Principal:' part
        snippet_text = re.sub(r'(Principal|Acting Principal)\W*', '',
                              snippet_text, flags=re.IGNORECASE).strip()
        principal_name = snippet_text

    return principal_name, principal_email

def extract_principal(soup):
    """
    Look for the first tag that contains "Principal" text,
    then parse out the principal name & email.
    """
    principal_tags = find_principal_tags(soup)
    if principal_tags:
        # pick the first one
        return parse_principal_info(principal_tags[0])
    return None, None

def parse_school_page(url):
    """
    Given a school website URL, attempt to retrieve the principal name, principal email,
    phone number, general school email, and school address from the page's HTML.
    Returns a tuple: (principal_name, principal_email, phone, school_email, address).
    If any value is missing or cannot be found, returns None for that field.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/109.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return (None, None, None, None, None)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1) Principal
    principal_name, principal_email = extract_principal(soup)

    # 2) "SCHOOL INFORMATION" block
    info_block = extract_school_info_block(soup)
    phone, school_email, address = None, None, None
    if info_block:
        phone, school_email, address = parse_info_block(info_block)

    return principal_name, principal_email, phone, school_email, address


def main():
    # 1. Load the CSV output from the previous script
    input_csv = 'school_directory.csv'
    df = pd.read_csv(input_csv)

    # Prepare new columns
    principal_names = []
    principal_emails = []
    phones = []
    school_emails = []
    addresses = []

    # 2. Iterate over each row
    for idx, row in df.iterrows():
        website_url = row.get('Website', None)
        if pd.isna(website_url) or not isinstance(website_url, str) or not website_url.startswith('http'):
            # If no valid website
            principal_names.append(None)
            principal_emails.append(None)
            phones.append(None)
            school_emails.append(None)
            addresses.append(None)
            continue

        # 3. Scrape the page
        principal, p_email, phone, s_email, addr = parse_school_page(website_url)

        principal_names.append(principal)
        principal_emails.append(p_email)
        phones.append(phone)
        school_emails.append(s_email)
        addresses.append(addr)

    # 4. Add new columns to df
    df['Principal'] = principal_names
    df['Principal_Email'] = principal_emails
    df['Phone'] = phones
    df['School_Email'] = school_emails
    df['School_Address'] = addresses

    # 5. Save final data to CSV
    output_csv = 'school_directory_with_details.csv'
    df.to_csv(output_csv, index=False)
    print(f"Saved updated data to {output_csv}")

if __name__ == '__main__':
    main()