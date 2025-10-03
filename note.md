```
This dataset is 100% synthetic.

The following parts were simulated:
    - Prices: generated from a base price with weekly variations of ±10%. 
    - Promotions: applied in ~30% of cases with discounts of 5–20% and random time windows. 
    - Availability: assigned probabilistically (70% in_stock, 20% out_of_stock, 10% preorder). 
    - Condition: 90% new, 5% refurb, 5% used.
    - Top-10 models per brand: statically selected in the script (MODEL_CATALOG dictionary).

How real data could be obtained in later phases:
    1. Implement web scraping on Fnac and Boulanger.
        - Fnac: https://www.fnac.com/Ordinateurs-portables/shi48967/w-4
        - Boulanger: https://www.boulanger.com/c/tous-les-ordinateurs-portables
    2. Technical scraping:
        - Use requests + BeautifulSoup.
    3. Fields to extract:
        - Retailer, brand, model, regular price, promotional price, availability, scraping date.
    4. Normalization:
        - Adapt the extracted data to the schema defined in file_schema.json.
    5. Integration:
        - Run the scraper weekly to generate historical snapshots.
        - Save in CSV/JSON for price and promotion analysis.

This deliverable is based on the ability to organize and simulate data in the required format. 
The same flow can be connected to real data with weekly scraping from Fnac and Boulanger, 
without changing the schema or the validation processes.
```
