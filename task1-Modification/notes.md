After the Task 1 tests, we were asked to normalize the data following the column structure from the example “Traditional_Segment_Top100Q2 (2)”:
Rank, Brand, CPU Brand, Processor Type, RAM, Storage, Screen Size, Resolution, Price, Product Name

To achieve this, two scripts were created:
    - Synthetic generator: Based on the generation.py code, it produces normalized, realistic-looking data without depending on any website.

    - Boulanger scraper: Extracts whatever actually exists on that store (via JSON-LD and HTML) and maps it to the normalized columns.
Note: different sites publish different metadata. Therefore, when a field from the example does not exist on the website, we leave it empty or use a clearly documented equivalent field.

Synthetic generator:
    - Code:
        - generate_modify.py
    - Run commands:
        - python generate_modify.py --retailer boulanger --n 100
        - python generate_modify.py --retailer fnac --n 100
    - Generated files:
        - synthesize_data_boulanger.csv
        - synthesize_data_fnac.csv

Boulanger scraper:
    - Code:
        - boulanger_scrapping.py
    - Run command:
        - python boulanger_scrapping.py
    - Generated files:
        - boulanger_scrapping
    - Notes:
        - Collects data from https://www.boulanger.com/c/tous-les-ordinateurs-portables.
        - Gathers product links under /ref/..., opens each product page, and extracts JSON-LD (@type=Product).
        - Fallsback to HTML/text if a field is missing in JSON-LD.
        - Normalizes units and formats (e.g., Go → GB for RAM; “SSD 512 Go MVMe” → “512GB SSD” for Storage).
        - For “Resolution,” the example uses labels like “FHD/2K/etc.”, but many Boulanger pages publish a numeric resolution (“1920 x 1080 pixels”). The script returns the normalized numeric form (“1920x1080”) when available. If not present, it remains empty.


About scraping Fnac: Scraping Fnac was not completed in this iteration because we could not connect to the site or read its robots.txt, but the thinking behind the Boulanger code to analyze the JSON-LD of a product to determine the parameters of interest and normalize it to our format would be quite similar.