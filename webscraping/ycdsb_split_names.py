import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv("yrdsb_school_profiles_with_emails.csv")  # or your CSV file name

# Split the Principal Name into FIRST and LAST columns
def split_principal_name(full_name):
    """
    Splits the principal's name into FIRST (first token)
    and LAST (all remaining tokens).
    Example:
      "John T. Smith" -> FIRST="John", LAST="T. Smith"
      "Angela McMahon" -> FIRST="Angela", LAST="McMahon"
    """
    if not isinstance(full_name, str):
        return "", ""  # Handle potential NaN or non-string cases
    
    tokens = full_name.strip().split()
    if len(tokens) == 0:
        return "", ""
    elif len(tokens) == 1:
        # If there's only one token, treat it as FIRST and leave LAST empty
        return tokens[0], ""
    else:
        # FIRST = first token, LAST = everything else
        first = tokens[0]
        last = " ".join(tokens[1:])
        return first, last

# Apply the split to create new columns
df["FIRST"], df["LAST"] = zip(*df["Principal"].apply(split_principal_name))

# Drop the original Principal Name column
df.drop(columns=["Principal"], inplace=True)

# Save the resulting DataFrame to a new CSV
df.to_csv("yrdsb_school_profiles_first_last.csv", index=False)

print("Successfully created 'yrdsb_school_profiles_first_last.csv' with FIRST and LAST columns (Principal removed).")