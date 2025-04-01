#!/usr/bin/env python3
"""
A module/script that finds CSV files matching a pattern and concatenates them into one DataFrame.
"""

import os
import glob
import pandas as pd
import argparse

def concat_csv_files(pattern="planet_waves_products*.csv", output_file="concatenated.csv"):
    """
    Find all CSV files matching the given `pattern`, concatenate them, and save to `output_file`.
    Returns the resulting DataFrame for further use if imported as a module.
    """
    # Search for all files matching the pattern
    csv_files = glob.glob(pattern)

    if not csv_files:
        print(f"No files found for pattern: {pattern}")
        return pd.DataFrame()  # Return empty DF if no files found

    # Read each file into a list of DataFrames
    dataframes = []
    for csv_file in csv_files:
        print(f"Reading {csv_file}")
        df = pd.read_csv(csv_file)
        dataframes.append(df)

    # Concatenate all DataFrames
    concatenated_df = pd.concat(dataframes, ignore_index=True)
    print(f"Concatenated {len(csv_files)} files.")

    # Save the result
    concatenated_df.to_csv(output_file, index=False)
    print(f"Saved concatenated DataFrame to: {output_file}")

    # Return the DataFrame in case this function is imported and called elsewhere
    return concatenated_df

def main():
    """
    Command-line usage:
        python concat_csv.py --pattern="planet_waves_products*.csv" --output="all_products.csv"
    """
    parser = argparse.ArgumentParser(
        description="Concatenate CSV files matching a given pattern into a single output file."
    )
    parser.add_argument(
        "--pattern",
        default="planet_waves_products*.csv",
        help="Glob pattern to match CSV files (default: planet_waves_products*.csv)."
    )
    parser.add_argument(
        "--output",
        default="concatenated.csv",
        help="Name of the output CSV file (default: concatenated.csv)."
    )

    args = parser.parse_args()
    concat_csv_files(pattern=args.pattern, output_file=args.output)

if __name__ == "__main__":
    main()