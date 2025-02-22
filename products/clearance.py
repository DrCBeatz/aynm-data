# clearance.py

# Script to combine multiple CSV files into a pandas dataframe and replace the text 'Used' or 
# 'Previously Rented' with 'Gently Used' in the 'Title' and 'Body (HTML)' columns.

import pandas as pd
import glob
import re

# 1. Load all matching CSV files. 
files = glob.glob('clearance?.csv')

# 2. Read each file into a DataFrame and then concatenate.
df_list = [pd.read_csv(f) for f in files]
df = pd.concat(df_list, ignore_index=True)

def fix_text(text, replacement="Gently Used"):
    """
    1) Replace 'previously rented' -> `replacement` (case-insensitive).
    2) Replace 'used' -> `replacement` (case-insensitive), 
       but skip if it's already preceded by 'gently' (any case + any amount of spaces).
    """
    if pd.isnull(text):
        return text  # if field is NaN

    # -- Step A: Replace 'previously rented' with chosen replacement
    text = re.sub(r'(?i)previously rented', replacement, text)

    # -- Step B: Replace 'used' except if preceded by 'gently' (any case/spaces)
    # We'll do this with a function to avoid variable-length lookbehind.
    pattern = re.compile(r'(?i)used')  # case-insensitive match for "used"
    
    def replace_used(m):
        start = m.start()
        # Grab some context before 'used'
        before_text = text[max(0, start-20):start]  # 20 chars is arbitrary padding
        # Check if it ends with "gently" (in any case) possibly followed by spaces
        # We'll do a small regex on `before_text` itself:
        if re.search(r'(?i)gently\s*$', before_text):
            # If the preceding text ends with "gently" + spaces, do NOT replace
            return m.group(0)  # just return "used" as-is
        else:
            return replacement
    
    # Perform the second replacement using our custom function
    text = re.sub(pattern, replace_used, text)

    return text

# 3. Apply fix_text with different replacements depending on the column
for col in ['Title', 'Body (HTML)']:
    if col in df.columns:
        if col == 'Title':
            # In Title, use all uppercase "GENTLY USED"
            df[col] = df[col].astype(str).apply(lambda x: fix_text(x, replacement="GENTLY USED"))
        else:
            # In Body, use "Gently Used"
            df[col] = df[col].astype(str).apply(lambda x: fix_text(x, replacement="Gently used"))



# 4. (Optional) Save the result to a new CSV, if desired
df.to_csv('clearance_combined.csv', index=False)