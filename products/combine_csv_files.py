# combine_csv_files.py

import argparse
import pandas as pd
import glob

def combine_csv_files(file_name_pattern: str, output_filename: str = "output_file.csv", **kwargs):
    """
    Combine all CSV files matching a given filename pattern into a single CSV file.

    Parameters:
    -----------
    file_name_pattern : str
        The glob pattern to match CSV files (e.g., 'products_export-*.csv').
    output_filename : str, optional
        The name of the output CSV file. Defaults to 'output_file.csv'.
    """
    csv_files = glob.glob(file_name_pattern)

    if not csv_files:
        print(f"No files found for pattern: {file_name_pattern}")
        return

    data_frames = [pd.read_csv(file, **kwargs) for file in csv_files]
    first_cols = set(data_frames[0].columns)

    if any(set(df.columns) != first_cols for df in data_frames[1:]):
        print("Warning: Not all files have the same columns. The final CSV may have mismatched data.")

    combined_df = pd.concat(data_frames, ignore_index=True)
    combined_df.to_csv(output_filename, index=False)
    print(f"Combined {len(csv_files)} files into {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combine all CSV files matching a given filename pattern into a single CSV."
    )

    parser.add_argument(
        "file_name_pattern",
        help="The glob pattern to match CSV files (e.g., 'products_export-*.csv')"
    )

    parser.add_argument(
        "output_filename",
        nargs="?",
        default="output_file.csv",
        help="Name of the output CSV file (default: output_file.csv)"
    )

    args = parser.parse_args()

    combine_csv_files(
        file_name_pattern=args.file_name_pattern,
        output_filename=args.output_filename
    )