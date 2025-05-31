# kawartha_pineridge_extract_schools.py

from bs4 import BeautifulSoup
import pandas as pd
import re, textwrap, os

# ↓ 1)  PASTE YOUR FULL HTML BETWEEN THE TRIPLE-QUOTES  ↓
html_content = """
"""

soup = BeautifulSoup(html_content, "html.parser")
records = []

def debug(msg):
    """Simple helper so you can comment-out ALL debug lines at once."""
    print(msg)

for tab in soup.select("p.tab > a.nav-link"):
    school  = tab.get_text(strip=True)
    collapse_id = tab.get("href", "").lstrip("#")
    details = soup.find("div", id=collapse_id)
    if not details:
        debug(f"[WARN] No details div for {school}")
        continue

    # ---------- Address & Phone ----------
    first_p = details.find("p")
    address = phone = ""
    if first_p:
        phone_link = first_p.find("a", href=lambda x: x and x.startswith("tel"))
        if phone_link:
            phone = phone_link.get_text(strip=True)
            phone_link.extract()                      # remove so it's not in address
        address = " ".join(first_p.stripped_strings)

    # ---------- Principal name & email ----------
    principal = principal_email = ""

    # 1) Find any tag whose text *includes* “Principal”
    cand_tags = [t for t in details.find_all(text=re.compile(r"Principal", re.I))]
    # 2) Walk up to the containing element (<p>, <div>, etc.)
    cand_tags = [t.parent for t in cand_tags]

    for tag in cand_tags:
        # Look for an <a href="mailto:…"> INSIDE that tag
        mailto = tag.find("a", href=lambda x: x and x.lower().startswith("mailto:"))
        if mailto:
            principal_email = mailto["href"].replace("mailto:", "").strip()
            principal = mailto.get_text(strip=True)
            break        # first reasonable hit wins
        else:
            # Fallback: strip label and take text after “Principal:”
            text_after_label = re.sub(r"Principal\s*:\s*", "", tag.get_text(" ", strip=True), flags=re.I)
            # Could be “Name, Vice-Principal: …” → keep only first comma-separated item
            principal = text_after_label.split(",")[0].strip()
            if principal:
                break

    # ---------- School website ----------
    site_link = (details.find("a", string=re.compile(r"Link to.*school website", re.I)) or
                 details.find("a", string=re.compile(r"School website", re.I)))
    website = site_link["href"].strip() if site_link else ""

    # ---------- Debug print ----------
    debug(f"---- {school} ----")
    debug(f"  Address  : {address}")
    debug(f"  Phone    : {phone}")
    debug(f"  Principal: {principal}")
    debug(f"  Email    : {principal_email}")
    debug(f"  Website  : {website}\n")

    records.append({
        "School name"    : school,
        "Address"        : address,
        "Phone #"        : phone,
        "Principal"      : principal,
        "Principal email": principal_email,
        "Website url"    : website,
    })

df = pd.DataFrame(records)
out_path = "peterborough_schools.csv"
df.to_csv(out_path, index=False)
print(f"\n✅ Done — {len(df)} schools written to {out_path}")