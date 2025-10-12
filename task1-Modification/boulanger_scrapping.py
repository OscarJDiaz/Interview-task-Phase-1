import json
import re
import unicodedata
from html import unescape
from urllib.parse import urljoin

import requests
import pandas as pd
from bs4 import BeautifulSoup

CATEGORY_URL = "https://www.boulanger.com/c/tous-les-ordinateurs-portables"
HEADERS = {"User-Agent": "Mozilla/5.0"}
LIMIT = 100
OUTCSV = "boulanger_scrapping.csv"

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser"), r.url

def first_product_links(soup, base_url, limit=3):
    seen, out = set(), []
    for a in soup.select('a[href^="/ref/"]'):
        href = (a.get("href") or "").split("#")[0]
        if not href:
            continue
        full = urljoin(base_url, href)
        if full in seen:
            continue
        seen.add(full)
        out.append(full)
        if len(out) >= limit:
            break
    return out

def strip_accents(s):
    s = s or ""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def norm_key(s):
    s = unescape(s or "").lower().strip()
    s = strip_accents(s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def product_jsonld(soup):
    found = []
    for tag in soup.select('script[type="application/ld+json"]'):
        raw = tag.string or tag.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue

        def yield_products(obj):
            if isinstance(obj, dict):
                if obj.get("@type") == "Product":
                    yield obj
                if "@graph" in obj and isinstance(obj["@graph"], list):
                    for it in obj["@graph"]:
                        if isinstance(it, dict) and it.get("@type") == "Product":
                            yield it
            elif isinstance(obj, list):
                for it in obj:
                    if isinstance(it, dict) and it.get("@type") == "Product":
                        yield it

        for it in yield_products(data):
            found.append(it)
    return found

def title_brand(s):
    if not s: return ""
    s = str(s).strip()
    if s.upper() in {"HP", "ASUS", "ACER", "MSI", "LG", "IBM", "RCA"}:
        return s.upper()
    return s[:1].upper() + s[1:].lower()

def parse_inches_from_text(s):
    if not s: return ""
    t = unescape(s)
    t = strip_accents(t)
    t = t.replace(",", ".")
    t = t.replace("”", '"').replace("“", '"').replace("''", '"')
    patterns = [
        r'(\d{1,2}(?:\.\d)?)\s*(?:po|pouces?|")',
        r'(\d{1,2}(?:\.\d)?)\s*(?:inch|inches?)',
        r'(\d{1,2}(?:\.\d)?)\s*(?:p|pce?)'
    ]
    for pat in patterns:
        m = re.search(pat, t, flags=re.IGNORECASE)
        if m:
            val = float(m.group(1))
            out = f"{val:.1f}".rstrip("0").rstrip(".")
            return f"{out} inch"
    m = re.search(r'(\d{1,2}(?:\.\d)?)\s*\(\s*\d{1,2}(?:\.\d)?\s*cm\)', t, flags=re.IGNORECASE)
    if m:
        val = float(m.group(1))
        out = f"{val:.1f}".rstrip("0").rstrip(".")
        return f"{out} inch"
    m = re.search(r'(\d{1,2}(?:\.\d)?)\s*["]', t)
    if m:
        val = float(m.group(1))
        out = f"{val:.1f}".rstrip("0").rstrip(".")
        return f"{out} inch"
    return ""

def to_gb_number(val):
    if not val: return None
    s = unescape(str(val)).lower()
    s = strip_accents(s).replace(",", ".")
    m = re.findall(r"(\d+(?:\.\d+)?)\s*(to|tb|tera|go|gb|g|gigaoctet|gigabyte)?", s)
    if not m: return None
    best_gb = 0.0
    for num, unit in m:
        numf = float(num)
        unit = unit or ""
        if unit in ["to", "tb", "tera"]:
            gb = numf * 1024.0
        else:
            gb = numf
        if gb > best_gb:
            best_gb = gb
    return best_gb if best_gb > 0 else None

def gb_to_compact(gb):
    if gb is None: return ""
    if gb >= 1024:
        tb = gb / 1024.0
        s = f"{tb:.1f}".rstrip("0").rstrip(".")
        return f"{s}TB"
    else:
        s = f"{gb:.0f}" if abs(gb - round(gb)) < 0.05 else f"{gb:.1f}".rstrip("0").rstrip(".")
        return f"{s}GB"

def normalize_ram(val):
    gb = to_gb_number(val)
    return f"{gb_to_compact(gb)} RAM" if gb else ""

def normalize_storage(val_type_cap, val_type_only, val_cap_only):
    text = " ".join([x for x in [val_type_cap, val_type_only, val_cap_only] if x])
    if not text: return ""
    lower = strip_accents(text.lower())

    stype = "SSD" if "ssd" in lower else ("HDD" if "hdd" in lower or "sata" in lower else "")

    m_all = re.findall(r"(\d+(?:[\.,]\d+)?)\s*(to|tb|tera|go|gb|g)\b", lower)
    best_gb = None
    for num, unit in m_all:
        num = num.replace(",", ".")
        numf = float(num)
        if unit in ["to", "tb", "tera"]:
            gb = numf * 1024.0
        else:
            gb = numf
        best_gb = gb if (best_gb is None or gb > best_gb) else best_gb

    cap = gb_to_compact(best_gb) if best_gb else ""

    if not cap:
        gb = to_gb_number(text)
        cap = gb_to_compact(gb) if gb else ""

    if cap and stype:
        return f"{cap} {stype}"
    return cap or text.strip()

def derive_cpu_brand(proc_type):
    if not proc_type:
        return ""
    s = proc_type.strip().lower()
    if s.startswith("intel"): return "Intel"
    if s.startswith("amd"): return "AMD"
    if s.startswith("apple"): return "Apple"
    return proc_type.split()[0].capitalize()

def normalize_resolution(val):
    if not val: return ""
    t = str(val)
    t2 = strip_accents(t.lower()).replace("×", "x")
    m = re.search(r"(\d+)\s*[x]\s*(\d+)", t2)
    if not m:
        return re.sub(r"\s+", " ", t).strip()
    w, h = int(m.group(1)), int(m.group(2))
    W, H = (w, h) if w >= h else (h, w)
    return f"{W}x{H}"

def normalize_price(prod):
    offers = prod.get("offers")
    price = ""
    if isinstance(offers, dict):
        price = offers.get("price") or ""
    elif isinstance(offers, list):
        for of in offers:
            if isinstance(of, dict) and of.get("price"):
                price = of["price"]
                break
    s = re.sub(r"[^\d]", "", str(price))
    return s

def extract_screen_size(prod, props_norm):
    keys = [
        "taille de l ecran en pouces diagonale",
        "taille de l ecran",
        "taille ecran",
        "taille de l ecran pouces",
        "taille de l ecran diagonale",
        "diagonale de l ecran",
        "diagonale ecran"
    ]
    for k in keys:
        if k in props_norm:
            got = parse_inches_from_text(props_norm[k])
            if got:
                return got
    for k, v in props_norm.items():
        if ("taille" in k or "diagonale" in k) and "ecran" in k:
            got = parse_inches_from_text(v)
            if got:
                return got
    for field in ["name", "description"]:
        got = parse_inches_from_text(prod.get(field) or "")
        if got:
            return got
    offers = prod.get("offers", {})
    if isinstance(offers, dict):
        got = parse_inches_from_text(offers.get("name", "") or offers.get("description", ""))
        if got:
            return got
    return ""

def extract_fields(prod):
    name = unescape(prod.get("name") or "").strip()

    brand = prod.get("brand")
    if isinstance(brand, dict):
        brand = brand.get("name") or brand.get("brand") or ""
    elif not isinstance(brand, str):
        brand = ""
    brand = title_brand(brand)

    additional = prod.get("additionalProperty") or prod.get("additionalProperties") or []
    props_norm = {}
    if isinstance(additional, list):
        for ap in additional:
            if isinstance(ap, dict):
                k = norm_key(ap.get("name", ""))
                v = unescape(str(ap.get("value", ""))).strip()
                if k:
                    props_norm[k] = v

    proc_type = ""
    for key in ["processeur", "reference du processeur", "processeur cpu", "reference processeur"]:
        if key in props_norm:
            proc_type = props_norm[key].strip()
            break

    cpu_brand = derive_cpu_brand(proc_type)

    ram_raw = ""
    for key in ["memoire vive ram", "memoire vive", "ram"]:
        if key in props_norm:
            ram_raw = props_norm[key]
            break
    ram = normalize_ram(ram_raw)

    type_cap = props_norm.get("type et capacite totale de stockage", "")
    type_only = ""
    for key in ["type de stockage", "stockage", "support de stockage"]:
        if key in props_norm:
            type_only = props_norm[key]; break
    cap_only = ""
    for key in ["capacite de stockage", "capacite totale de stockage"]:
        if key in props_norm:
            cap_only = props_norm[key]; break
    storage = normalize_storage(type_cap, type_only, cap_only)

    screen = extract_screen_size(prod, props_norm)

    resolution_raw = props_norm.get("resolution") or props_norm.get("definition de l image") or ""
    resolution = normalize_resolution(resolution_raw)

    price = normalize_price(prod)

    return {
        "Brand": brand,
        "CPU Brand": cpu_brand,
        "Processor Type": proc_type,
        "RAM": ram,
        "Storage": storage,
        "Screen Size": screen,
        "Resolution": resolution,
        "Price": price,
        "Product Name": name,
    }


def main():
    cat_soup, resolved = get_soup(CATEGORY_URL)
    base = f"{resolved.split('/',3)[0]}//{resolved.split('/',3)[2]}"
    links = first_product_links(cat_soup, base, limit=LIMIT)
    if not links:
        print("No product links found.")
        return

    rows = []
    for purl in links:
        try:
            psoup, _ = get_soup(purl)
            blocks = product_jsonld(psoup)
            if not blocks:
                continue
            prod = blocks[0]
            rows.append(extract_fields(prod))
        except Exception:
            continue

    df = pd.DataFrame(rows, columns=[
        "Brand","CPU Brand","Processor Type","RAM","Storage","Screen Size","Resolution","Price","Product Name"
    ])
    df.insert(0, "Rank", range(1, len(df) + 1))
    df.to_csv(OUTCSV, index=False, encoding="utf-8")
    print(f"CSV guardado en {OUTCSV} con {len(df)} filas.")

if __name__ == "__main__":
    main()
