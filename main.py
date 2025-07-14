import requests
from bs4 import BeautifulSoup
import json
import logging
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

BASE_URL = "https://ca.myprotein.com"
CATEGORY_URL = "https://ca.myprotein.com/c/nutrition/protein/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

def fetch_product_links():
    logging.info("Fetching product links from category page...")
    response = requests.get(CATEGORY_URL, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/p/sports-nutrition/'):
            links.add(BASE_URL + href)
    logging.info(f"Found {len(links)} product links")
    return sorted(links)


def extract_product_data(url):
    logging.info(f"Fetching product page: {url}")
    try:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    script_tag = soup.find('script', attrs={"data-track": "productVisit"})
    if not script_tag:
        logging.error(f"Product data script tag not found for {url}")
        return None

    script_content = script_tag.string
    if not script_content:
        logging.error(f"No script content found in productVisit tag for {url}")
        return None

    try:
        start_key = "const masterData = "
        start_idx = script_content.find(start_key)
        if start_idx == -1:
            logging.error(f"masterData JSON not found in script for {url}")
            return None
        start_idx += len(start_key)
        end_idx = script_content.find("};", start_idx)
        if end_idx == -1:
            logging.error(f"End of masterData JSON not found for {url}")
            return None
        end_idx += 1  # include the closing brace

        master_data_json_str = script_content[start_idx:end_idx]
        master_data = json.loads(master_data_json_str)
    except Exception as e:
        logging.error(f"Error parsing masterData JSON for {url}: {e}")
        return None

    product_title = master_data.get("pageTitle")
    variants = master_data.get("variants", [])

    variant_data_list = []

    for variant in variants:
        sku = variant.get("sku")
        title = variant.get("title", "")
        in_stock = variant.get("inStock", False)
        price_info = variant.get("price", {})
        price = price_info.get("price", {}).get("amount", "")
        display_price = price_info.get("price", {}).get("displayValue", "")
        rrp = price_info.get("rrp", {}).get("amount", "")
        display_rrp = price_info.get("rrp", {}).get("displayValue", "")

        sale_price = ""
        if rrp and price and float(price) < float(rrp):
            sale_price = display_price

        # Parse Size and Flavor from variant title string (split by " - ")
        parts = title.split(" - ")
        size = ""
        flavor = ""
        if len(parts) >= 3:
            size = parts[1].strip()
            flavor = parts[2].strip()
        elif len(parts) == 2:
            size = parts[1].strip()

        variant_data_list.append({
            "Product Name": product_title,
            "SKU": sku,
            "Variant Title": title,
            "Flavor": flavor,
            "Size": size,
            "Price": display_price,
            "Sale Price": sale_price,
            "Original Price": display_rrp,
            "In Stock": "Yes" if in_stock else "No",
            "Product URL": url
        })

    return variant_data_list


def main():
    product_links = fetch_product_links()
    all_variants = []

    max_workers = 7
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_product_data, url): url for url in product_links}

        for future in as_completed(futures):
            url = futures[future]
            try:
                variants = future.result()
                if variants:
                    all_variants.extend(variants)
                    logging.info(f"Processed {url} with {len(variants)} variants")
                else:
                    logging.warning(f"No variant data for {url}")
            except Exception as e:
                logging.error(f"Error processing {url}: {e}")

    csv_headers = [
        "Product Name", "SKU", "Variant Title", "Flavor", "Size",
        "Price", "Sale Price", "Original Price", "In Stock", "Product URL"
    ]

    csv_filename = "myprotein_variants.csv"

    if all_variants:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(all_variants)

        logging.info(f"Saved variant data for {len(all_variants)} variants to {csv_filename}")
    else:
        logging.info("No variant data to save.")


if __name__ == "__main__":
    main()
