# Autor: Oscar Díaz

import random
import string
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List, Dict, Any

RANDOM_SEED = 42
NUM_WEEKS = 4
RETAILERS = ["Fnac", "Boulanger"]
ALL_BRANDS = ["HP", "Lenovo", "Dell", "Apple", "ASUS", "Samsung", "Acer"]
NUM_BRANDS = 7
BRANDS = ALL_BRANDS[:NUM_BRANDS]

def midnight_utc(d: datetime) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)

ANCHOR_DAY = midnight_utc(datetime.now(timezone.utc))

def week_starts_list(anchor_day_utc: datetime, n_weeks: int) -> List[datetime]:
    base = anchor_day_utc - timedelta(weeks=n_weeks - 1)
    return [base + timedelta(weeks=i) for i in range(n_weeks)]

AVAIL_CHOICES = ["in_stock", "out_of_stock", "preorder"]
AVAIL_WEIGHTS = [0.70, 0.20, 0.10]

COND_CHOICES = ["new", "refurb", "used"]
COND_WEIGHTS = [0.90, 0.05, 0.05]

CURRENCY = "EUR"

MODEL_CATALOG = {
    "HP": [
        "Envy 13", "Pavilion 14", "Spectre x360", "Omen 16", "Victus 15",
        "ProBook 440", "EliteBook 840", "ZBook Firefly", "Chromebook x2", "Dragonfly G4"
    ],
    "Lenovo": [
        "ThinkPad X1 Carbon", "Yoga Slim 7", "IdeaPad 5", "Legion 5", "ThinkBook 14",
        "LOQ 15", "ThinkPad T14", "Yoga 7", "IdeaPad Flex 5", "Slim 7 Pro"
    ],
    "Dell": [
        "XPS 13", "XPS 15", "Inspiron 14", "Inspiron 16", "Latitude 7440",
        "Vostro 3520", "G15", "Alienware m16", "Precision 3580", "Chromebook 3110"
    ],
    "Apple": [
        "MacBook Air M2", "MacBook Pro 14 M3", "MacBook Pro 16 M3", "MacBook Air 13 M1", "MacBook Pro 13 M2",
        "MacBook Air M3", "MacBook Pro 14 M2", "MacBook Air 15 M2", "MacBook Pro 16 M2", "MacBook Air 13 M3"
    ],
    "ASUS": [
        "Zenbook 14 OLED", "Vivobook 15", "ROG Zephyrus G14", "TUF Gaming A15", "ExpertBook B5",
        "Chromebook Flip CX5", "ProArt Studiobook", "ROG Strix G16", "Vivobook S14", "Zenbook S 13"
    ],
    "Samsung": [
        "Galaxy Book3", "Galaxy Book3 Pro", "Galaxy Book4", "Galaxy Book2 360", "Galaxy Book3 Ultra",
        "Galaxy Book Go", "Galaxy Book3 360", "Galaxy Book Flex2", "Galaxy Book Ion", "Galaxy Book4 Pro"
    ],
    "Acer": [
        "Swift 3", "Swift Go 14", "Aspire 5", "Nitro 5", "Predator Helios 16",
        "Spin 5", "Chromebook Spin 713", "TravelMate P4", "Swift X 14", "Aspire Vero"
    ],
}

PRICE_RANGES = {
    "HP": (600, 2200),
    "Lenovo": (550, 2200),
    "Dell": (600, 2400),
    "Apple": (1100, 3500),
    "ASUS": (550, 2500),
    "Samsung": (700, 2600),
    "Acer": (450, 2000),
}

def iso_date(d: datetime) -> str:
    return d.date().isoformat()

def iso_dt(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def normalize_model_id(brand: str, model_name: str) -> str:
    s = f"{brand} {model_name}".upper()
    allowed = string.ascii_uppercase + string.digits + " "
    s = "".join(ch if ch in allowed else " " for ch in s)
    tokens = "-".join(t for t in s.split() if t)
    return tokens

def sample_installment(price: float) -> Optional[float]:
    if random.random() < 0.60:
        return round(price / 4.0, 2)
    return None

def promo_window_for_week(week_start_dt: datetime) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
    if random.random() >= 0.30:
        return None, None, None
    start_offset_days = random.randint(-3, 3)
    promo_start = week_start_dt + timedelta(days=start_offset_days, hours=random.randint(0, 20))
    duration_days = random.randint(2, 10)
    promo_end = promo_start + timedelta(days=duration_days, hours=random.randint(0, 20))
    promo_type = random.choice(["flash_sale", "clearance", "back_to_school", "weekend_deal"])
    return promo_start, promo_end, promo_type

def promo_price_from(price: float) -> Optional[float]:
    if random.random() < 0.80:
        disc = random.uniform(0.05, 0.20)
        return round(price * (1 - disc), 2)
    return None

def compute_rank_within_brand(df: pd.DataFrame) -> pd.DataFrame:
    df["rank_within_brand"] = (
        df.groupby(["retailer", "brand", "week_start"])["price"]
          .rank(method="first", ascending=True)
          .astype(int)
    )
    return df

def main() -> None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    records: List[Dict[str, Any]] = []
    week_starts = week_starts_list(ANCHOR_DAY, NUM_WEEKS)

    base_prices: Dict[Tuple[str, str], float] = {}

    for week_dt in week_starts:
        for retailer in RETAILERS:
            for brand in BRANDS:
                price_min, price_max = PRICE_RANGES[brand]
                model_names = MODEL_CATALOG[brand][:10]  # top-10
                for model_name in model_names:
                    model_id = normalize_model_id(brand, model_name)

                    key = (brand, model_id)
                    if key not in base_prices:
                        base_prices[key] = round(random.uniform(price_min, price_max), 2)

                    drift = random.uniform(-0.10, 0.10)
                    price = max(0.0, round(base_prices[key] * (1 + drift), 2))

                    installment_price = sample_installment(price)

                    promo_start_dt, promo_end_dt, promo_type = promo_window_for_week(week_dt)
                    if promo_start_dt and promo_end_dt:
                        promo_price = promo_price_from(price)
                        promo_active = (promo_price is not None) and (promo_start_dt <= week_dt <= promo_end_dt)
                        promo_start = iso_dt(promo_start_dt)
                        promo_end = iso_dt(promo_end_dt)
                    else:
                        promo_price = None
                        promo_active = False
                        promo_start = None
                        promo_end = None
                        promo_type = None

                    record = {
                        "retailer": retailer,
                        "brand": brand,
                        "model_id": model_id,
                        "model_name": model_name,
                        "condition": random.choices(COND_CHOICES, weights=COND_WEIGHTS, k=1)[0],
                        "week_start": iso_date(week_dt),
                        "price": price,
                        "promo_price": promo_price,
                        "installment_price": installment_price,
                        "promo_start": promo_start,
                        "promo_end": promo_end,
                        "promo_type": promo_type,
                        "promo_active": bool(promo_active),
                        "prev_week_price": None,
                        "price_change_abs": None,
                        "price_change_pct": None,
                        "rank_within_brand": None,
                        "availability_status": random.choices(AVAIL_CHOICES, weights=AVAIL_WEIGHTS, k=1)[0],
                        "currency": CURRENCY,
                        "scraped_at": iso_dt(week_dt + relativedelta(hours=random.randint(7, 18)))
                    }
                    records.append(record)

    df = pd.DataFrame(records)

    df["week_start_dt"] = pd.to_datetime(df["week_start"], format="%Y-%m-%d", utc=True)
    df = df.sort_values(by=["retailer", "brand", "model_id", "week_start_dt"]).reset_index(drop=True)

    df["prev_week_price"] = (
        df.groupby(["retailer", "brand", "model_id"])["price"]
          .shift(1)
          .round(2)
    )

    df["price_change_abs"] = (df["price"] - df["prev_week_price"]).round(2)
    df.loc[df["prev_week_price"].isna(), "price_change_abs"] = np.nan

    df["price_change_pct"] = (100 * df["price_change_abs"] / df["prev_week_price"]).round(2)
    df.loc[df["prev_week_price"].isna() | (df["prev_week_price"] == 0), "price_change_pct"] = np.nan

    df = compute_rank_within_brand(df)

    columns = [
        "retailer","brand","model_id","model_name","condition","week_start","price","promo_price",
        "installment_price","promo_start","promo_end","promo_type","promo_active","prev_week_price",
        "price_change_abs","price_change_pct","rank_within_brand","availability_status","currency","scraped_at"
    ]
    df = df[columns]

    df.to_csv("dataset.csv", index=False)
    df.to_json("dataset.json", orient="records", force_ascii=False, indent=2)

    rows_expected = len(BRANDS) * 10 * len(RETAILERS) * NUM_WEEKS
    print("Generation Summary:")
    print(f"   Brands: {len(BRANDS)} → {BRANDS}")
    print(f"   Retailers: {RETAILERS}")
    print(f"   Weeks: {NUM_WEEKS} (from {df['week_start'].min()} to {df['week_start'].max()})")
    print(f"   Rows generated: {len(df)} (expected: {rows_expected})")
    print("   Files:")
    print("   - dataset.csv")
    print("   - dataset.json")

if __name__ == "__main__":
    main()
