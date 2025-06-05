#!/usr/bin/env python3
"""
product_sale.py – mark products “on-sale”, set type to Clearance, copy
Variant Price ➜ Variant Compare At Price, and discount Variant Price by 15 %.

USAGE
-----
    python product_sale.py input.csv
    python product_sale.py input.csv -o output.csv

If -o/--output is omitted, the script writes <input>_updated.csv
in the same directory as the source file.
"""

from pathlib import Path
import argparse
import sys

import pandas as pd


# ----------------------------- helpers -------------------------------- #
def add_onsale(tags_cell: str) -> str:
    """Ensure the tag list contains 'on-sale' (handles NaN / empty)."""
    if pd.isna(tags_cell) or not str(tags_cell).strip():
        return "on-sale"

    tags_list = [t.strip() for t in str(tags_cell).split(",") if t.strip()]
    if "on-sale" not in tags_list:
        tags_list.append("on-sale")
    return ",".join(tags_list)


# ------------------------------ main ---------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply clearance-sale transformations to a Shopify-style CSV"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the CSV file to transform"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Where to write the transformed CSV "
             "(default: <input>_updated.csv next to the source)"
    )

    args = parser.parse_args()
    inp: Path = args.input
    out: Path = args.output or inp.with_name(f"{inp.stem}_updated{inp.suffix}")

    if not inp.is_file():
        sys.exit(f"Error: {inp} does not exist or is not a file.")

    # Read with Variant SKU / Barcode preserved as strings
    df = pd.read_csv(
        inp,
        dtype={
            "Variant SKU": str,
            "Variant Barcode": str
        }
    )

    # 1. Tag products as on-sale
    df["Tags"] = df["Tags"].apply(add_onsale)

    # 2. Set Type to Clearance
    df["Type"] = "Clearance"

    # 3. Copy Variant Price ➜ Variant Compare At Price
    df["Variant Compare At Price"] = df["Variant Price"]

    # 4. Discount Variant Price by 10 %
    df["Variant Price"] = pd.to_numeric(
        df["Variant Price"], errors="coerce"
    ) * 0.9

    # 5. Write result
    df.to_csv(out, index=False)
    print(f"✅  Updated CSV written to: {out}")


if __name__ == "__main__":
    main()
