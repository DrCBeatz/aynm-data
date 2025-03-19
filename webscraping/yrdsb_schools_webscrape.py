import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def parse_school_card(article):
    """
    Extracts relevant information from a single school card (<article>).
    Returns a dictionary of the extracted data.
    """
    data = {
        "School Name": None,
        "Principal": None,
        "Phone Number": None,  
        "Website": None,
        "Street Address": None,
        "City": None,
        "Province": None,
        "Postal Code": None,
    }
    
    # 1) School Name
    name_tag = article.select_one("h2.font-weight-bold span")
    if name_tag:
        data["School Name"] = name_tag.get_text(strip=True)
    
    # 2) Principal Name
    principal_tag = article.select_one("div.field--name-field-principal p")
    if principal_tag:
        data["Principal"] = principal_tag.get_text(strip=True)
    
    # 3) Phone Number (only the first one)
    phone_div = article.select_one("div.field--name-field-phone")
    if phone_div:
        phone_links = phone_div.select("a[href^='tel:']")
        # If there's at least one telephone link, grab the first one only
        if phone_links:
            phone_text = phone_links[0].get_text(strip=True)
            # e.g. "Tel: (905) 709-3554" — remove "Tel:" to keep just the number
            phone_text = phone_text.replace("Tel:", "").strip()
            data["Phone Number"] = phone_text
    
    # 4) Website URL (look for link text "Website link")
    link_candidates = article.select("a.school-profile-card-link")
    for link in link_candidates:
        link_text = link.get_text(strip=True)
        if "Website link" in link_text:
            data["Website"] = link.get("href")
            break
    
    # 5) Address
    address_tag = article.select_one("p.address")
    if address_tag:
        street_span = address_tag.select_one("span.address-line1")
        if street_span:
            data["Street Address"] = street_span.get_text(strip=True)
        
        city_span = address_tag.select_one("span.locality")
        if city_span:
            data["City"] = city_span.get_text(strip=True)
        
        province_span = address_tag.select_one("span.administrative-area")
        if province_span:
            data["Province"] = province_span.get_text(strip=True)
        
        postal_span = address_tag.select_one("span.postal-code")
        if postal_span:
            data["Postal Code"] = postal_span.get_text(strip=True)
    
    return data
def get_total_pages(soup):
    """
    Reads the pagination links to find the maximum page number.
    We’ll look for <ul class="pager__items"> and find the last numbered page.
    """
    pagination = soup.select_one("ul.pager__items")
    if not pagination:
        return 1  # No pagination, only 1 page
    
    page_links = pagination.select("li.pager__item a")
    
    # Extract all the page=? numbers from the links
    page_numbers = []
    for link in page_links:
        href = link.get("href", "")
        # href might look like "?page=2" -> get the number at the end
        if "page=" in href:
            # split by '='
            _, page_num = href.split("=")
            # Attempt to convert to int
            try:
                page_numbers.append(int(page_num))
            except ValueError:
                pass
    
    # The maximum we found + 1 pages might exist, but typically this should be the last page
    return max(page_numbers) + 1 if page_numbers else 1

def scrape_yrdsb_schools(base_url):
    """
    Scrapes the entire set of school profile pages on the YRDSB site.
    Returns a list of dictionaries containing the school data.
    """
    # 1. First request to get the total number of pages
    response = requests.get(base_url)
    if not response.ok:
        print("Failed to retrieve the first page.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    all_schools = []
    
    resp = requests.get(base_url)
    if not resp.ok:
        print(f"Skipping page; could not retrieve data.")
    
    page_soup = BeautifulSoup(resp.text, "html.parser")
    
    # 3. Each school is contained in an <article class="school-profiles-container">
    school_articles = page_soup.select("article.school-profiles-container")
    for article in school_articles:
        school_data = parse_school_card(article)
        all_schools.append(school_data)
    
    # Throttle requests slightly to be polite
    time.sleep(1)

    return all_schools

def main():
    # This is the main URL that shows the first page of school profiles
    base_url = "http://127.0.0.1:5500/york_region_district_schoolboard.html"
    
    # Scrape all school data
    schools_list = scrape_yrdsb_schools(base_url)
    
    # Convert the list of dicts to a DataFrame
    df = pd.DataFrame(schools_list)
    
    # Export to CSV
    df.to_csv("yrdsb_school_profiles.csv", index=False)
    print("Data saved to yrdsb_school_profiles.csv")

if __name__ == "__main__":
    main()