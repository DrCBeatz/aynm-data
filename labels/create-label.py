import shutil
import argparse
from compress import compress
import pandas as pd
from replace import nth_repl_all, replace_file_text

# Default CSV file name
DEFAULT_INPUT_FILE = 'products_export.csv'
output_file = "label.xml"
sale = False
source_file = 'template_sale.xml' if sale else 'template_reg.xml'
lbx_files = ['label.xml', 'prop.xml', 'Object0.bmp']
title_string = """[TITLE]"""
i = 0

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create a label from a CSV file.')
    parser.add_argument('-f', '--file', type=str, default=DEFAULT_INPUT_FILE, help='CSV file to use for creating the label')
    args = parser.parse_args()

    input_file = args.file

    # Copy the template file to the output file
    shutil.copyfile(source_file, output_file)

    # Read the CSV file
    df = pd.read_csv(input_file, dtype={'Variant SKU': str, 'Variant Barcode': str, 'Variant Price': str, 'Variant Compare At Price': str})

    # Update the label contents
    new_title = nth_repl_all(df.iloc[i]['Title'], " ", "\n", 2)
    replace_file_text('[SKU]', df.iloc[i]['Variant SKU'])
    replace_file_text('[VENDOR]', df.iloc[i]['Vendor'])
    replace_file_text(title_string, new_title)

    if sale:
        replace_file_text('[reg-pr]', str(df.iloc[i]['Variant Compare At Price']))
        replace_file_text('[sale-pr]', str(df.iloc[i]['Variant Price']))
    else:
        replace_file_text('[reg-pr]', str(df.iloc[i]['Variant Price']))

    replace_file_text('010101010101', str(df.iloc[i]['Variant Barcode']))
    upc_length = len(str(df.iloc[i]['Variant Barcode']))
    replace_file_text('lengths="12"', f'lengths="{str(upc_length)}"')

    # Compress the label files
    compress(lbx_files)

    print('Label created')

if __name__ == '__main__':
    main()