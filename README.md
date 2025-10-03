```
This project generates a synthetic dataset of laptop prices sold by Fnac and Boulanger.

Project Structure

/Interview task — Phase 1
|-- dev_plan.md
|-- README.md
|-- generation.py
|-- dataset.csv
|-- dataset.json
|-- validation.py

Requirements: /n
    - Python 3.8 or higher

Dependencies:
    - pip install pandas numpy python-dateutil

Required Fields:
    - Each record includes the following fields:
        - retailer                   →     Fnac or Boulanger
        - brand                      →     HP, Lenovo, Dell, Apple, ASUS, Samsung, Acer
        - model_id                   →     normalized uppercase identifier with hyphens (example: "HP-ENVY-13")
        - model_name                 →     commercial model name (example: "Envy 13")
        - condition                  →     product status: new, used, refurb
        - week_start                 →     ISO date (YYYY-MM-DD) indicating the start of the week
        - price                      →     regular price (decimal)
        - promo_price                →     promotional price (decimal or null)
        - installment_price          →     installment price (decimal or null)
        - promo_start / promo_end    →     ISO dates for promotion start and end (or null)
        - promo_type                 →     promotion type (example: flash_sale)
        - promo_active               →     boolean, true if week_start is within the range [promo_start, promo_end] and promo_price exists
        - prev_week_price            →     price from the previous week (decimal or null)
        - price_change_abs           →     absolute difference from the previous week (decimal or null)
        - price_change_pct           →     percentage difference from the previous week (decimal or null)
        - rank_within_brand          →     model ranking within its brand (1 to 10)
        - availability_status        →     availability status: in_stock, out_of_stock, preorder
        - currency                   →     always "EUR"
        - scraped_at                 →     ISO date and time when the snapshot was taken    

Simulation Rules:
    - 7 brands × 10 models × 2 retailers × 4 weeks = 560 rows.
    - Base price per model with weekly variations of ±10%.
    - Promotion in ~30% of cases, with discounts of 5–20%.
    - Availability distribution: 70% in_stock, 20% out_of_stock, 10% preorder.
    - Condition distribution: 90% new, 5% refurb, 5% used.
    - Fixed currency in "EUR".

Selection of Top-10 models per brand
    - As in Phase 1 no real scraping is performed, the Top-10 selection is synthetic but plausible.
    - For each brand (HP, Lenovo, Dell, Apple, ASUS, Samsung, Acer) 10 representative models of the recent catalog were listed, using their commercial availability as a proxy of “latest 10 by timestamp”.
    - The list of 10 models per brand is fixed in the Generation script (MODEL_CATALOG) for reproducibility.
    - In an implementation with real data, the “latest 10 by timestamp” would be obtained by sorting by listing date on Fnac/Boulanger
    and taking the 10 most recent per brand.

Execution:
    - python generation.py
    - python validation.py
```

Outputs:
    - generation.py → generates dataset.csv and dataset.json.
    - validation.py → validates that the dataset complies with business rules.


