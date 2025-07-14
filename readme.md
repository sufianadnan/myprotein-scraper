
# MyProtein Product Variant Scraper

This Python project scrapes product variant data from the **MyProtein Canada** website, specifically from the protein nutrition category. It extracts detailed product variant information including SKU, flavor, size, price, sale price, and stock availability, then exports the data into a CSV file for easy analysis.

---

## Purpose

I built this scraper to compare protein product sizes, serving portions, and prices to help find the best value for money (best bang for your buck) when purchasing protein supplements from MyProtein Canada.

---

## Features

- Automatically fetches all product links from the MyProtein protein nutrition category.
- Extracts detailed product variant information from each product page.
- Parses variant title to break down **flavor** and **size/serving** separately.
- Captures pricing details including sale price and original price.
- Multithreaded requests for faster scraping.
- Exports data cleanly to a CSV file for further analysis.

---

## Requirements

- Python 3.7+
- Requests
- BeautifulSoup4

Install dependencies with:

```bash
pip install requests beautifulsoup4
```

---

## Usage

Run the scraper with:

```bash
python scraper.py
```

It will generate a `myprotein_variants.csv` file in the working directory containing the following columns:

- Product Name
- SKU
- Variant Title
- Flavor
- Size
- Price
- Sale Price
- Original Price
- In Stock (Yes/No)
- Product URL

You can then open the CSV in Excel, Google Sheets, or any data analysis tool to compare products by size, flavor, and price.

---

## Notes

- The scraper uses a custom User-Agent header to avoid being blocked.
- Data is parsed from embedded JavaScript JSON (`masterData` object) on the product pages.
- Size and Flavor are extracted from the variant title by splitting the string format like:  
  `Product Name - Size - Flavor`

---

## License

This project is open source and free to use under the MIT License.

Happy scraping and good luck finding the best protein deals! 💪🥤
