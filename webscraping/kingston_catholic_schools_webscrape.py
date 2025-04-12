# kingston_catholic_schools_webscrape.py

import pandas as pd
from bs4 import BeautifulSoup

html_content = """-- input HTML content here --
"""

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# We'll store each school's data as a dictionary in this list
schools_data = []

# Each school entry is wrapped in a 'div' with class 'collapsible-block'
collapsible_blocks = soup.find_all("div", class_="collapsible-block")

for block in collapsible_blocks:
    # 1. Extract the School Name
    header = block.find("div", class_="collapsible-header")
    if not header:
        # If there's no header, skip this block
        continue
    
    # The school name is typically inside a <strong> tag within the header
    strong_tag = header.find("strong")
    if strong_tag:
        school_name = strong_tag.get_text(strip=True)
    else:
        # Fallback if no <strong> found
        school_name = header.get_text(strip=True)
    
    # 2. Extract content area
    content = block.find("div", class_="collapsible-content")
    if not content:
        # If there's no content area, skip
        continue
    
    # Grab all text within the collapsible-content
    text_lines = [
        line.strip()
        for line in content.get_text(separator="\n").split("\n")
        if line.strip()
    ]
    
    # Prepare placeholders
    phone = None
    address = None
    website = None
    
    # 3. Find Telephone and Address
    #    - Usually the pattern is:
    #      Telephone: XXX
    #      Fax: XXX
    #      ADDRESS LINE
    #
    # We look for the line that starts with 'Telephone:' and assume
    # the Address line is typically after 'Fax:' or right after phone if no fax line.
    
    phone_idx = None
    for i, line in enumerate(text_lines):
        if "Telephone:" in line:
            phone_idx = i
            break
    
    if phone_idx is not None:
        # Extract the phone number
        phone_line = text_lines[phone_idx]
        # e.g., "Telephone: 613-962-7541"
        phone = phone_line.replace("Telephone:", "").strip()
        
        # Check if next line is "Fax:"
        # If so, address is likely the line after the fax
        if phone_idx + 1 < len(text_lines) and "Fax:" in text_lines[phone_idx + 1]:
            if phone_idx + 2 < len(text_lines):
                address = text_lines[phone_idx + 2]
        else:
            # If there's no "Fax:" line next, address might be the very next line
            if phone_idx + 1 < len(text_lines):
                next_line = text_lines[phone_idx + 1]
                # If it doesn't contain 'Fax:' or 'Telephone:', we can consider it the address
                if "Fax:" not in next_line and "Telephone:" not in next_line:
                    address = next_line
    
    # 4. Find the Website (Look for the link with "Visit Website" text)
    link_tag = content.find("a", text=lambda t: t and "Visit Website" in t)
    if link_tag:
        website = link_tag.get("href", None)
    
    # 5. Append results
    school_info = {
        "School Name": school_name,
        "Address": address,
        "Phone Number": phone,
        "Website": website
    }
    schools_data.append(school_info)

# 6. Create a Pandas DataFrame and display it
df = pd.DataFrame(schools_data)
print(df)

df.to_csv('kingston_catholic_schools.csv', index=False)