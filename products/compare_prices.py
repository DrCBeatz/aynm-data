#!/usr/bin/env python3
"""
Compare prices between profile_products_combined.csv (original)
and profile_products_combined_updated.csv (updated).

Adds detailed logging so you can confirm:
  • shape of both data‑frames
  • duplicate‑key counts for Variant SKU
  • presence of required columns
"""

import logging
from pathlib import Path
import pandas as pd
from pandas.errors import MergeError

# ----------------------------------------------------------------------
ORIG_FILE    = "profile_products_combined.csv"
UPDATED_FILE = "profile_products_combined_updated.csv"
DIFF_FILE    = "profile_products_price_differences.csv"
# ----------------------------------------------------------------------

# ---- basic logging setup ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

def load_df(path: Path, name: str) -> pd.DataFrame:
    """Load a product CSV with critical ID columns forced to string."""
    logging.info(f"Loading {name} data‑frame from {path.name!r}")
    df = pd.read_csv(
        path,
        dtype={
            "Variant SKU": "string",
            "Variant Barcode": "string",
        },
        keep_default_na=False
    )
    logging.info(f"{name} shape: {df.shape}")
    dup = df["Variant SKU"].duplicated().sum()
    logging.info(f"{name}: {dup:,} duplicate Variant SKU value(s)")
    return df

def check_columns(df: pd.DataFrame, cols: list[str], name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"{name} is missing required column(s): {missing}")

def main() -> None:
    cwd = Path.cwd()
    # 1) ---------------------------------------------------------------------
    df_orig = load_df(cwd / ORIG_FILE, "ORIGINAL")
    df_upd  = load_df(cwd / UPDATED_FILE, "UPDATED")

    # quick sanity on columns we’ll use later
    key_cols = ["Variant Price", "Cost per item"]
    check_columns(df_orig, key_cols, "ORIGINAL")
    check_columns(df_upd,  key_cols, "UPDATED")

    # 2) ---------------------------------------------------------------------
    try:
        merged = pd.merge(
            df_orig,
            df_upd,
            on="Variant SKU",
            suffixes=("_orig", "_upd"),
            how="inner",
            # validate="one_to_one"
        )
        logging.info(f"Merged df shape: {merged.shape}")
    except MergeError as e:
        logging.error("Merge failed because keys aren’t unique.")
        logging.error(str(e))
        logging.info(
            "Hint: run again without 'validate=\"one_to_one\"' or "
            "deduplicate Variant SKU values first."
        )
        return

    # 3) ---------------------------------------------------------------------
    price_changed = merged["Variant Price_orig"] != merged["Variant Price_upd"]
    cost_changed  = merged["Cost per item_orig"] != merged["Cost per item_upd"]
    any_changed   = price_changed | cost_changed

    diff_df = merged.loc[any_changed, [
        "Variant SKU",
        "Variant Price_orig", "Variant Price_upd",
        "Cost per item_orig", "Cost per item_upd",
    ]]

    # 4) ---------------------------------------------------------------------
    diff_df.to_csv(cwd / DIFF_FILE, index=False)

    logging.info(
        f"Found {len(diff_df):,} product(s) with different Variant Price "
        f"or Cost per item."
    )
    logging.info(f"Details written to {DIFF_FILE!r}")

    if not diff_df.empty:
        logging.info("\nFirst few differences:\n%s",
                     diff_df.to_string(index=False))

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()