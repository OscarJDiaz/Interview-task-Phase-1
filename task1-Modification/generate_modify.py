import argparse
import random
import string
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd

RANDOM_SEED = random.randint(1, 9999)
DEFAULT_N = 100

BRANDS = ["HP", "Lenovo", "Dell", "Apple", "ASUS", "Samsung", "Acer"]

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

CPU_INTEL = [
    "Intel Processor N100",
    "Intel Core i3-1215U",
    "Intel Core i5-12450H",
    "Intel Core i5-1334U",
    "Intel Core i7-1360P",
    "Intel Core i7-13700H"
]
CPU_AMD = [
    "AMD Ryzen 3 7320U",
    "AMD Ryzen 5 7530U",
    "AMD Ryzen 5 7640HS",
    "AMD Ryzen 7 7735HS",
    "AMD Ryzen 7 7840U"
]
CPU_APPLE = [
    "Apple M1",
    "Apple M2",
    "Apple M3",
    "Apple M3 Pro",
    "Apple M3 Max"
]

RAM_OPTIONS = ["4GB RAM", "8GB RAM", "16GB RAM", "32GB RAM"]
STORAGE_OPTIONS = ["128GB Flash", "256GB SSD", "512GB SSD", "1TB SSD", "2TB SSD"]
SCREEN_SIZES = ["13.3 inch", "14 inch", "15.6 inch", "16 inch"]
RESOLUTIONS = ["HD", "FHD", "2K", "QHD", "UHD"]

def cpu_for_brand(brand: str) -> Tuple[str, str]:
    """
    Devuelve (cpu_brand, processor_type) coherente con la marca.
    Apple → Apple, otros → Intel/AMD
    """
    if brand == "Apple":
        proc = random.choice(CPU_APPLE)
        return ("Apple", proc)
    else:
        if random.random() < 0.65:
            proc = random.choice(CPU_INTEL)
            return ("Intel", proc)
        else:
            proc = random.choice(CPU_AMD)
            return ("AMD", proc)

def synth_price(brand: str) -> float:
    lo, hi = PRICE_RANGES[brand]
    x = np.random.beta(2, 3)
    price = lo + x * (hi - lo)
    return round(float(price), 2)

def make_product_name(brand: str, model: str, screen: str, res: str, ram: str, storage: str, cpu: str) -> str:
    base = f"{brand} {model}"
    details = f"{screen} {res} | {ram} | {storage} | {cpu}"
    return f"{base} | {details}"

def generate_rows(n: int, retailer: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    per_brand = max(1, n // len(BRANDS))
    leftover = n - per_brand * len(BRANDS)

    brand_plan = []
    for b in BRANDS:
        brand_plan.extend([b] * per_brand)
    for _ in range(leftover):
        brand_plan.append(random.choice(BRANDS))

    random.shuffle(brand_plan)

    for brand in brand_plan:
        model = random.choice(MODEL_CATALOG[brand])
        cpu_brand, proc_type = cpu_for_brand(brand)
        ram = random.choice(RAM_OPTIONS)
        storage = random.choice(STORAGE_OPTIONS)
        screen = random.choice(SCREEN_SIZES)
        res = random.choice(RESOLUTIONS)
        price = synth_price(brand)

        product_name = make_product_name(
            brand=brand,
            model=model,
            screen=screen,
            res=res,
            ram=ram,
            storage=storage,
            cpu=proc_type
        )

        row = {
            "Brand": brand,
            "CPU Brand": cpu_brand,
            "Processor Type": proc_type,
            "RAM": ram,
            "Storage": storage,
            "Screen Size": screen,
            "Resolution": res,
            "Price": price,
            "Product Name": product_name,
        }
        rows.append(row)

    return rows

def main():
    parser = argparse.ArgumentParser(description="Genera Traditional_Segment para un retailer.")
    parser.add_argument("--retailer", type=str, help="Nombre del retailer (ej: Fnac o Boulanger).")
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="Número de filas a generar (default 100).")
    parser.add_argument("--out", type=str, default=None, help="Nombre de archivo de salida (CSV).")
    args = parser.parse_args()

    retailer = args.retailer
    if not retailer:
        retailer = input("Introduce el retailer (ej: Fnac, Boulanger): ").strip() or "Retailer"

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    rows = generate_rows(args.n, retailer)
    df = pd.DataFrame(rows)

    df = df.sort_values(by=["Price", "Brand", "Product Name"], ascending=[True, True, True]).reset_index(drop=True)
    df.insert(0, "Rank", df.index + 1)

    cols = ["Rank", "Brand", "CPU Brand", "Processor Type", "RAM", "Storage", "Screen Size", "Resolution", "Price", "Product Name"]
    df = df[cols]

    out_csv = args.out or f"synthesize_data_{retailer}.csv"
    df.to_csv(out_csv, index=False)
    print(f"✅ Archivo generado: {out_csv}")
    print(f"   Filas: {len(df)} | Columnas: {len(df.columns)}")
    print(df.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
