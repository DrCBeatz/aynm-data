import pandas as pd
import re

def generate_email_from_principal(principal_name):
    """
    Takes a principal's full name (e.g. "Chris Moscato", "Jennifer DeCoff")
    and returns [first].[last]@niagaracatholic.ca in lowercase.

    If the name has more than two words (e.g. "Chris J. Moscato"), we take
    the first token as the first name, and the last token as the last name.
    If the name is missing or only 1 token, returns an empty string.
    """
    if not principal_name or not principal_name.strip():
        return ""

    parts = principal_name.split()
    if len(parts) < 2:
        return ""  # Can't form an email if we only have one name

    first_name = parts[0]
    last_name = parts[-1]

    # Remove punctuation, convert to lowercase, etc.
    first_name_clean = re.sub(r"[^\w]+", "", first_name).lower()
    last_name_clean = re.sub(r"[^\w]+", "", last_name).lower()

    if not first_name_clean or not last_name_clean:
        return ""

    return f"{first_name_clean}.{last_name_clean}@niagaracatholic.ca"

if __name__ == "__main__":
    csv_filename = "niagra_catholic_schoolboard_updated.csv"
    df = pd.read_csv(csv_filename)

    # Create or overwrite the "email" column
    df["email"] = df["principal"].apply(generate_email_from_principal)

    # Save the updated CSV
    output_filename = "niagra_catholic_schoolboard_with_emails.csv"
    df.to_csv(output_filename, index=False)
    print(f"Updated CSV saved to {output_filename}")
