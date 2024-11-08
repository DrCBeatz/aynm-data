# names_script.py

from names_txt import names_txt
import pandas as pd

df = pd.DataFrame(columns=['Name', 'Email', 'Phone'])
names_list = names_txt.split('\n\n')


for name in names_list:
    entry_list = name.split('\n')
    row = []
    try:
        print(f"Name: {entry_list[0].split(':')[1].strip()}")
        row.append(entry_list[0].split(':')[1].strip())
    except:
        row.append(' ')

    try:
        print(f"Email: {entry_list[1].split(':')[1].strip()}")
        row.append(entry_list[1].split(':')[1].strip())
    except:
        row.append(' ')

    try:
        print(f"Phone: {entry_list[2].split(':')[1].strip()}")
        row.append(entry_list[2].split(':')[1].strip())
    except:
        row.append(' ')
    df.loc[len(df)] = row
    print('\n')

print(df)
df.to_csv('draw.csv', index=False)
