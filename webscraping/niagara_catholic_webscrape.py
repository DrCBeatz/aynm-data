import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape_niagra_catholic_info(url):
    """
    This function attempts to scrape 'Contact Info' (address, phone)
    and 'Principal' from the page at the given URL.
    It returns a dictionary with keys: address, phone, principal.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # -- Find the paragraph containing "Contact Info" --
    contact_info_paragraph = None
    for p in soup.find_all("p"):
        strong_tag = p.find("strong")
        # We do a case-insensitive search for "contact info"
        if strong_tag and re.search(r"contact\s*info", strong_tag.get_text(), re.IGNORECASE):
            contact_info_paragraph = p
            break

    address, phone = "", ""
    if contact_info_paragraph:
        lines = [x.strip() for x in contact_info_paragraph.get_text(separator="\n").split("\n") if x.strip()]

        # Find phone (line starting with 'Ph:' ignoring case)
        for line in lines:
            if line.lower().startswith("ph:"):
                phone = line.replace("Ph:", "").strip()
                break

        # Build address: lines after "Contact Info" up to "Ph:"
        collect = False
        address_lines = []
        for line in lines:
            if re.search(r"contact\s*info", line, re.IGNORECASE):
                collect = True
                continue
            if line.lower().startswith("ph:"):
                break
            if collect:
                address_lines.append(line)
        address = ", ".join(address_lines)

    # -- Find the paragraph with "Principal" --
    principal = ""
    principal_paragraph = None
    for p in soup.find_all("p"):
        strong_tag = p.find("strong")
        if strong_tag and re.search(r"principal", strong_tag.get_text(), re.IGNORECASE):
            principal_paragraph = p
            break

    if principal_paragraph:
        principal_lines = [x.strip() for x in principal_paragraph.get_text(separator="\n").split("\n") if x.strip()]
        if len(principal_lines) > 1:
            principal = principal_lines[1]

    # Return results as a dict
    return {
        "address": address,
        "phone": phone,
        "principal": principal
    }

if __name__ == "__main__":
    # CSV filename
    csv_filename = 'niagra_catholic_schoolboard.csv'

    # 1. Read the CSV into a DataFrame
    df = pd.read_csv(csv_filename)

    # We'll create three new columns in the DataFrame: address, phone, principal
    df["address"] = ""
    df["phone"] = ""
    df["principal"] = ""

    # 2. Iterate over each row in the DataFrame, using the 'Website' column
    for idx, row in df.iterrows():
        url = row["Website"]
        print(f"Processing row {idx}: {url}")

        # If the URL is missing or invalid, you might skip:
        if not isinstance(url, str) or not url.startswith("http"):
            print("  Skipping: invalid URL")
            continue

        try:
            # 3. Scrape data
            result = scrape_niagra_catholic_info(url)
            # 4. Append data to the DataFrame row
            df.at[idx, "address"] = result["address"]
            df.at[idx, "phone"] = result["phone"]
            df.at[idx, "principal"] = result["principal"]
        except Exception as e:
            print(f"  ERROR scraping {url}: {e}")
            # Optionally leave these columns blank or set an error message

    # 5. Save the updated DataFrame back to CSV
    #    (or you could just print df)
    output_filename = "niagra)catholic_schoolboard_updated.csv"
    df.to_csv(output_filename, index=False)
    print(f"\nUpdated CSV saved to {output_filename}")

