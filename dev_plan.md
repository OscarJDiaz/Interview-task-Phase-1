Day 1 — Design & sample definition

    - Objective: 
        - Define a schema in JSON format with all required fields and create a sample CSV file with 2–3 rows.

    - Deliverables:  
        - file_schema.json (data structure).  
        - dataset.csv (sample rows).  

    - Acceptance criteria:  
        - The schema includes all required fields.  
        - The CSV file contains data consistent with the schema.  
        - Basic generation rules are documented (e.g., how `model_id` is calculated, when `promo_active` is set).  

Day 2 — Data generation script

    - Objective: 
        - Create a script that generates synthetic data automatically following the schema.  

    - Deliverables:  
        - generation.py (script).  
        - dataset.csv (minimum dataset).  
        - dataset.json (equivalent copy).  

    - Acceptance criteria:
        - The script generates 80 rows (1 brand × 10 models × 2 retailers × 4 weeks).  
        - All fields comply with the schema.  
        - CSV and JSON files open without errors.  

Day 3 — Full dataset generation

    - Objective:  
        - Scale the script to generate the full dataset with all brands and save the final result.  

    - Deliverables:
        - generation.py (extended script).  
        - dataset.csv (final dataset).  
        - dataset.json (equivalent copy).  

    - Acceptance criteria:  
        - The dataset generates 560 rows (7 brands × 10 models × 2 retailers × 4 weeks = 560 rows).  
        - All dates in ISO format.  
        - Data is consistent and reproducible.  

Day 4 — Validation & basic calculations

    - Objective:  
        - Validate weekly calculations and the quality of the final dataset.  

    - Deliverables:
        - validation.py (validation script).  
        - Validation report (console or assertions).  

    - Acceptance criteria:  
        - prev_week_price, price_change_abs, price_change_pct, and rank_within_brand are correct.  
        - No missing values in mandatory fields.  
        - The dataset contains at least 560 rows.  

Day 5 — Documentation & submission package

    - Objective: 
        - Package the project and document the final delivery.  

    - Deliverables:  
        - README.md with usage instructions.  
        - dev_plan.md (this document).  
        - Generation and validation scripts.  
        - Dataset files (`dataset.csv/json`).  
        - A 1-page explanatory note on how real data could be obtained from Fnac/Boulanger in later phases.  

    - Acceptance criteria: 
        - Reproducible submission.  
        - Dataset with all fields in ISO format.  
        - Clear documentation.  

