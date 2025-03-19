import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def extract_email_from_website(url):
    """
    Given a school's website URL, return the email address found
    under the 'Contact Information' section (the 'mailto:' link).
    Return None if no email is found or if there's an error.
    """
    # Basic sanity check:
    if not url or not isinstance(url, str) or not url.startswith("http"):
        return None
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except (requests.RequestException, ValueError):
        # If there's any error in fetching the page, return None
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # --- Strategy A: Look for the anchor with 'mailto:' in href
    #     that appears *after* a "Contact Information" heading or text.
    #     We'll try a broad approach: any mailto: link near 'Contact Information'
    
    # 1) Find a tag that contains "Contact Information".
    #    Sometimes it is in a <div> or other block with text:
    contact_info_elem = None
    possible_headers = soup.find_all(
        lambda tag: tag.name in ["div", "h1", "h2", "h3", "h4"] 
        and "Contact Information" in tag.get_text(strip=True)
    )
    
    if not possible_headers:
        # fallback: maybe just look for *any* 'mailto:' link on the page
        mailto_link = soup.find("a", href=lambda h: h and h.startswith("mailto:"))
        if mailto_link:
            return mailto_link.get_text(strip=True)
        else:
            return None
    else:
        # Use the first match
        contact_info_elem = possible_headers[0]
    
    # 2) From there, search for an <a href="mailto:..."> 
    #    in the same parent or next siblings
    parent_container = contact_info_elem.parent
    
    # If the same block holds the mailto link, check:
    mailto = parent_container.find("a", href=lambda h: h and h.startswith("mailto:"))
    if mailto:
        return mailto.get_text(strip=True)
    
    # Alternatively, check contact_info_elem’s next siblings:
    # This is optional if your pages have a slightly different structure
    sibling = contact_info_elem.find_next_sibling()
    while sibling:
        mailto_sibling = sibling.find("a", href=lambda h: h and h.startswith("mailto:"))
        if mailto_sibling:
            return mailto_sibling.get_text(strip=True)
        sibling = sibling.find_next_sibling()
    
    # If none found in the above approach, fallback:
    mailto_link = soup.find("a", href=lambda h: h and h.startswith("mailto:"))
    if mailto_link:
        return mailto_link.get_text(strip=True)
    
    return None


def main():
    # Load the CSV previously created
    df = pd.read_csv("yrdsb_school_profiles.csv")
    
    # Create a new column "Email" by iterating over the Website URLs
    emails = []
    for index, row in df.iterrows():
        website_url = row.get("Website", None)
        print(f"Processing row {index+1} / {len(df)}: {row['School Name']}...")
        
        email = extract_email_from_website(website_url)
        emails.append(email)
        
        # Short delay to avoid hammering the server
        time.sleep(1)
    
    df["Email"] = emails
    
    # Save the updated data to a new CSV
    df.to_csv("yrdsb_school_profiles_with_emails.csv", index=False)
    print("Saved updated CSV with Email column: yrdsb_school_profiles_with_emails.csv")

if __name__ == "__main__":
    main()