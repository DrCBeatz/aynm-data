import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_school_table(url, table_id):
    """
    Scrape the table with the given table_id from the specified url.
    Returns a pandas DataFrame with columns: ['School Name', 'Grades', 'Email', 'Website'].
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/109.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Raise an HTTPError if status != 200

    soup = BeautifulSoup(response.text, 'html.parser')

    # Then proceed as before...
    table = soup.find('table', {'id': table_id})
    if not table:
        print(f"No table found with id: {table_id}")
        return pd.DataFrame()

    # (rest of the logic remains the same)
    school_names = []
    grades_list = []
    emails = []
    websites = []

    tbody = table.find('tbody')
    if not tbody:
        print(f"No <tbody> found in table {table_id}")
        return pd.DataFrame()

    rows = tbody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        
        # Column 1: school name
        school_col = cols[0]
        school_link = school_col.find('a')
        school_name = school_link.get_text(strip=True) if school_link else school_col.get_text(strip=True)
        
        # Column 2: info text => Grades, Email, Website
        info_col = cols[1].get_text(separator=' ', strip=True)
        grades_chunk = info_col
        email_address = None
        website_url = None

        if 'Email:' in info_col:
            grades_chunk = info_col.split('Email:')[0].strip()

        # Check for mailto link
        mailto_link = cols[1].find('a', href=True, text=True)
        if mailto_link and 'mailto:' in mailto_link['href']:
            email_address = mailto_link.text.strip()

        # Check for website link
        links = cols[1].find_all('a', href=True)
        for link_tag in links:
            if link_tag['href'].startswith('http'):
                website_url = link_tag['href'].strip()
                break

        grades = grades_chunk.replace('Grade ', '').strip()

        school_names.append(school_name)
        grades_list.append(grades)
        emails.append(email_address)
        websites.append(website_url)

    df = pd.DataFrame({
        'School Name': school_names,
        'Grades': grades_list,
        'Email': emails,
        'Website': websites
    })
    return df

def main():
    url = 'https://www.ocsb.ca/our-schools/'
    table_id = 'tablepress-36-no-2'
    df = scrape_school_table(url, table_id)

    print(df.head())
    df.to_csv('school_directory.csv', index=False)
    print(f"Saved {len(df)} rows to 'school_directory.csv'")

if __name__ == "__main__":
    main()