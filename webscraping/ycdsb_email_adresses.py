import pandas as pd

def create_email(principal_name):
    """
    Given a principal name, e.g. "Angela McMahon",
    return an email address of the form "angela.mcmahon@ycdsb.ca".
    """
    # Strip any leading/trailing whitespace
    name = principal_name.strip()
    
    # Split on whitespace
    parts = name.split()
    
    if len(parts) < 2:
        # If we don't have at least two tokens, return empty or handle differently
        return ""
    
    # First name = first token
    first_name = parts[0].lower()
    # Last name = last token
    last_name = parts[-1].lower()
    
    # Construct the email
    email = f"{first_name}.{last_name}@ycdsb.ca"
    return email

# 1. Load the schools CSV file
df = pd.read_csv("ycdsb_schools.csv")

# 2. Create a new column for the principal's email
df["Principal Email"] = df["Principal Name"].apply(create_email)

# 3. Save the updated DataFrame to a new CSV
df.to_csv("ycdsb_schools_with_emails.csv", index=False)

print("Successfully created 'ycdsb_schools_with_emails.csv' with Principal Email column.")