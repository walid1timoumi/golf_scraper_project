from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import List

def parse_total_pages(html):
    soup = BeautifulSoup(html, "html.parser")
    pagination_links = soup.select("a.paging")
    page_numbers = [int(link.text.strip()) for link in pagination_links if link.text.strip().isdigit()]
    return max(page_numbers) if page_numbers else 1

def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")
    products_data = []

    products = soup.select("div.s-1-4.con")
    for product in products:
        name_tag = product.find("h3")
        price_tag = product.find("button", class_="price")
        link_tag = product.find("a", href=True)
        brand_tag = product.find("div", class_="mrg-10")
        offer_tag = product.find("div", class_="grn")

        product_name = name_tag.text.strip() if name_tag else "N/A"
        product_price = price_tag.find_all("span")[-1].text.strip() if price_tag else "N/A"
        product_link = "https://www.globalgolf.com" + link_tag["href"] if link_tag else "N/A"
        product_brand = brand_tag.text.strip() if brand_tag else "N/A"
        product_offer = offer_tag.text.strip() if offer_tag else "N/A"

        products_data.append([
            product_name,
            product_price,
            product_brand,
            product_link,
            product_offer
        ])

    return products_data

def parse_globalgolf(driver: WebDriver, config: dict) -> List[list]:
    all_products = []
    wait_time = config.get("wait_time", 3)
    base_url = config["base_url"]

    if "{page}" not in base_url:
        raise ValueError("❌ Config 'base_url' must contain '{page}' for pagination.")

    # Load first page and detect total pages
    print("\n🔍 Loading first page to detect pagination...")
    driver.get(base_url.replace("{page}", "1"))
    time.sleep(wait_time)

    html = driver.page_source
    total_pages = parse_total_pages(html)
    print(f"📄 Total pages detected: {total_pages}")

    for page in range(1, total_pages + 1):
        url = base_url.replace("{page}", str(page))
        print(f"\nScraping page {page}: {url}")
        try:
            driver.get(url)
            time.sleep(wait_time)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "s-1-4"))
            )

            page_html = driver.page_source
            page_products = parse_products(page_html)

            print(f"✅ Found {len(page_products)} products on page {page}")
            for product in page_products:
                all_products.append([page] + product)

        except Exception as e:
            print(f"❌ Error scraping page {page}: {e}")
            continue

    print(f"\n✅ GlobalGolf scraping complete. Pages: {total_pages}, Products: {len(all_products)}")
    return all_products
