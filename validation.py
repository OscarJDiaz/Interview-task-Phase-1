#Autor: Oscar Díaz

import pandas as pd
import numpy as np
from datetime import datetime
import sys

CSV_PATH = "dataset.csv"

REQUIRED_COLUMNS = [
    "retailer","brand","model_id","model_name","condition","week_start","price","promo_price",
    "installment_price","promo_start","promo_end","promo_type","promo_active","prev_week_price",
    "price_change_abs","price_change_pct","rank_within_brand","availability_status","currency","scraped_at"
]

def is_iso_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

def is_iso_datetime_z(s: str) -> bool:
    try:
        if s.endswith("Z"):
            datetime.fromisoformat(s.replace("Z", "+00:00"))
            return True
        datetime.fromisoformat(s)
        return True
    except Exception:
        return False

def main():
    df = pd.read_csv(CSV_PATH, dtype={"retailer": str, "brand": str, "model_id": str})

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    assert not missing_cols, f"Missing required columns: {missing_cols}"

    assert set(df["retailer"].unique()).issubset({"Fnac","Boulanger"}), "Retailer out of {Fnac,Boulanger}"
    assert set(df["brand"].unique()).issubset({"HP","Lenovo","Dell","Apple","ASUS","Samsung","Acer"}), "Brand out of list"
    assert set(df["availability_status"].dropna().unique()).issubset({"in_stock","out_of_stock","preorder"}), "availability_status invalid"
    assert set(df["condition"].dropna().unique()).issubset({"new","refurb","used"}), "condition invalid"
    assert set(df["currency"].dropna().unique()) == {"EUR"}, "currency debe ser siempre EUR"

    bad_week_start_fmt = df[~df["week_start"].astype(str).apply(is_iso_date)]
    assert bad_week_start_fmt.empty, f"week_start no ISO date in {len(bad_week_start_fmt)} rows"

    for col in ["promo_start","promo_end","scraped_at"]:
        mask = df[col].notna()
        bad = df.loc[mask & ~df[col].astype(str).apply(is_iso_datetime_z)]
        assert bad.empty, f"{col} no ISO datetime in {len(bad)} rows"

    for col in ["price","promo_price","installment_price","prev_week_price"]:
        mask = df[col].notna()
        bad = df.loc[mask & (df[col] < 0)]
        assert bad.empty, f"{col} have negative values in {len(bad)} rows"

    active = df[df["promo_active"] == True].copy()
    if not active.empty:
        no_pp = active[active["promo_price"].isna()]
        assert no_pp.empty, f"promo_active=True but promo_price is null in {len(no_pp)} rows"

        ps = pd.to_datetime(active["promo_start"], utc=True, errors="coerce")
        pe = pd.to_datetime(active["promo_end"], utc=True, errors="coerce")
        ws = pd.to_datetime(active["week_start"], format="%Y-%m-%d", utc=True)

        outside = active[(ps.isna()) | (pe.isna()) | (ws < ps) | (ws > pe)]
        assert outside.empty, f"promo_active=True but week_start is not in [promo_start,promo_end] in {len(outside)} rows"

    df_sorted = df.sort_values(by=["retailer","brand","model_id","week_start"])
    grp = df_sorted.groupby(["retailer","brand","model_id"])

    recomputed_prev = grp["price"].shift(1)
    dif_abs = (df_sorted["price"] - recomputed_prev).round(2)
    dif_pct = (100 * dif_abs / recomputed_prev).round(2)

    assert np.allclose(df_sorted["prev_week_price"].fillna(-999999), recomputed_prev.fillna(-999999)), "prev_week_price incorrectly calculated"
    mask_abs = ~(df_sorted["prev_week_price"].isna())
    assert np.allclose(df_sorted.loc[mask_abs, "price_change_abs"], dif_abs[mask_abs]), "price_change_abs incorrect"
    mask_pct = ~(df_sorted["prev_week_price"].isna() | (df_sorted["prev_week_price"] == 0))
    assert np.allclose(df_sorted.loc[mask_pct, "price_change_pct"], dif_pct[mask_pct]), "price_change_pct incorrect"

    rb = df.groupby(["retailer","brand","week_start"])["rank_within_brand"]
    out_of_range = df[(df["rank_within_brand"] < 1) | (df["rank_within_brand"] > 10)]
    assert out_of_range.empty, f"rank_within_brand out of 1..10 in {len(out_of_range)} rows"

    dups = rb.apply(lambda s: s.duplicated().sum()).sum()
    assert dups == 0, f"rank_within_brand duplicated within some (retailer,brand,week_start): {dups} duplicates"

    assert len(df) >= 560, f"Expected at least 560 rows; found {len(df)}"

    print("Validation completed.")
    print("Summary:")
    print(f"- Retailers: {sorted(df['retailer'].unique())}")
    print(f"- Brands: {sorted(df['brand'].unique())}")
    print(f"- Weeks: {df['week_start'].nunique()} (from {df['week_start'].min()} to {df['week_start'].max()})")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"VALIDATION FAILED: {e}")
        sys.exit(1)
