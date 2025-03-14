import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_text_or_empty(element):
    """Return stripped text from a BeautifulSoup element, or an empty string if None."""
    return element.get_text(strip=True) if element else ""

# ------------------------------------------------
# 1. FETCH THE PAGE
# ------------------------------------------------
url = "http://127.0.0.1:5500/ocsdb_schools.html"  # Replace with real URL
response = requests.get(url)
response.raise_for_status()  # Raise an error if the request failed

# ------------------------------------------------
# 2. PARSE WITH BEAUTIFUL SOUP
# ------------------------------------------------
soup = BeautifulSoup(response.text, "html.parser")

# ------------------------------------------------
# 3. SELECT ALL SCHOOL ITEMS
# ------------------------------------------------
all_schools = soup.select(".schools-list__item")
print(f"Found {len(all_schools)} .schools-list__item elements.")

# We will store results as a list of dicts
data = []

# ------------------------------------------------
# 4. LOOP OVER EACH SCHOOL ITEM
# ------------------------------------------------
for school_div in all_schools:
    # --- Extract direct info from the .schools-list__item ---

    # School Name
    name_el = school_div.select_one(".left h2")
    school_name = get_text_or_empty(name_el)

    # Grades
    grades_el = school_div.select_one(".left p.bold")
    raw_grades = get_text_or_empty(grades_el)
    # e.g. "Grades: JK-8"
    if "Grades:" in raw_grades:
        grades = raw_grades.replace("Grades:", "").strip()
    else:
        grades = raw_grades

    # Address (the first <li> not having the .phone class)
    address_el = school_div.select_one(".middle ul li:not(.phone)")
    address = get_text_or_empty(address_el)

    # Phone
    phone_el = school_div.select_one(".middle ul li.phone a")
    phone = get_text_or_empty(phone_el)

    # --- Find the corresponding modal (the next <dialog> after this div) ---
    # In your sample HTML, each <dialog> immediately follows the .schools-list__item.
    # We can use .find_next(...) to locate the next <dialog> with the given classes.
    modal = school_div.find_next("dialog", class_="single-school-article")

    email_address = ""
    website_url = ""

    if modal:
        # Email is in: <li class="email"><a href="mailto:...">Email</a></li>
        email_el = modal.select_one("li.email a[href^='mailto:']")
        if email_el:
            # The actual email is in the 'href' attribute, e.g. "mailto:alornecassidyes@ocdsb.ca"
            mailto = email_el.get("href", "")
            if mailto.startswith("mailto:"):
                email_address = mailto.replace("mailto:", "").strip()

        # Website is in: <a href="..." class="website-link" ...>
        website_link_el = modal.select_one("a.website-link")
        if website_link_el:
            website_url = website_link_el.get("href", "").strip()

    # --- Add the extracted data to our results ---
    data.append({
        "School Name": school_name,
        "Grades": grades,
        "Address": address,
        "Phone": phone,
        "Email": email_address,
        "Website": website_url
    })

# ------------------------------------------------
# 5. BUILD A PANDAS DATAFRAME
# ------------------------------------------------
df = pd.DataFrame(data)
print(df)

# Optionally, save results to CSV
df.to_csv("ocdsb_schools.csv", index=False)