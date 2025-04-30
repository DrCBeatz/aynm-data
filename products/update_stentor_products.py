#!/usr/bin/env python3
"""
update_stentor_products.py
──────────────────────────
Read stentor_products.csv and stentor_pricelist.csv,
update Variant Price & Cost per item, and write stentor_products_updated.csv
"""

from pathlib import Path
import pandas as pd

# ── File paths ────────────────────────────────────────────────────────────────
PROD_CSV  = Path("stentor_products.csv")
PRICE_CSV = Path("stentor_pricelist.csv")
OUT_CSV   = Path("stentor_products_updated.csv")

def main() -> None:
    # ── 1. Load source files ────────────────────────────────────────────────
    products = pd.read_csv(
        PROD_CSV,
        dtype={"Variant SKU": "string", "Variant Barcode": "string"},
        keep_default_na=False,
    )

    pricelist = pd.read_csv(
        PRICE_CSV,
        dtype={"Model": "string"},
        keep_default_na=False,
    )

    # ── 2. Normalise price columns (remove $, commas → float) ───────────────
    price_cols = ["2025 List", "Dealer"]

    for col in price_cols:
        pricelist[col] = (
            pricelist[col]
            .astype(str)                         # ensure string ops work
            .str.replace(r"[$,]", "", regex=True)  # strip symbols & commas
            .replace("", pd.NA)                  # empty strings → NA
            .astype(float)
        )

    # ── 3. Tidy keys & de-duplicate models if needed ────────────────────────
    pricelist["Model"] = pricelist["Model"].str.strip()
    pricelist = pricelist.drop_duplicates(subset="Model", keep="first")

    # ── 4. Merge pricelist into products on SKU/Model ───────────────────────
    merged = products.merge(
        pricelist[["Model", "2025 List", "Dealer"]],
        left_on="Variant SKU",
        right_on="Model",
        how="left",
        copy=False,
    )

    match_mask = merged["2025 List"].notna()

    # ── 5. Update price & cost on matched rows ──────────────────────────────
    merged.loc[match_mask, "Variant Price"] = merged.loc[match_mask, "2025 List"]
    merged.loc[match_mask, "Cost per item"] = merged.loc[match_mask, "Dealer"]

    # ── 6. Clean up helper columns & restore original order ─────────────────
    merged.drop(columns=["Model", "2025 List", "Dealer"], inplace=True)
    merged = merged[products.columns]          # exact original shape/order

    # ── 7. Reporting ────────────────────────────────────────────────────────
    updated_variants = merged.loc[match_mask, "Handle"]
    updated_count    = updated_variants.size
    updated_handles  = updated_variants.unique().tolist()

    print(f"✅ Updated {updated_count} product variant(s).")
    if updated_handles:
        for h in updated_handles:
            print(f"   • {h}")

    # ── 8. Save result ──────────────────────────────────────────────────────
    merged.to_csv(OUT_CSV, index=False)
    print(f"\n✍️  Saved updated catalogue to: {OUT_CSV.resolve()}")

if __name__ == "__main__":
    main()