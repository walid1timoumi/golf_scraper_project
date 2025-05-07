from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import time
from typing import List
import re

def close_popup(driver: WebDriver):
    try:
        time.sleep(2)
        close_button = driver.find_element(By.CLASS_NAME, "ltkpopup-close")
        close_button.click()
        print("✅ Closed popup")
    except:
        print("⏩ No popup to close")

def get_total_pages(soup: BeautifulSoup) -> int:
    try:
        count_span = soup.select_one("span.pagination-item__page-count")
        if count_span and "of" in count_span.text:
            return int(count_span.text.strip().split("of")[1].strip())
        return 1
    except:
        return 1

def extract_first_price(text):
    match = re.search(r"\$\d+[.,]?\d*", text)
    return match.group(0) if match else "N/A"

def parse_rockbottom(driver: WebDriver, config: dict) -> List[list]:
    base_url = config["base_url"]
    wait_time = config.get("wait_time", 3)
    all_products = []

    try:
        driver.get(base_url)
        close_popup(driver)
        time.sleep(wait_time)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        total_pages = min(get_total_pages(soup), config.get("max_pages", 50))
        print(f"🔢 Total pages found: {total_pages}")

        for page in range(1, total_pages + 1):
            url = f"{base_url}?page={page}" if page > 1 else base_url
            print(f"\n📄 Scraping page {page}: {url}")
            driver.get(url)
            time.sleep(wait_time)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            products = soup.select("li.product")
            print(f"✅ Found {len(products)} products")

            for prod in products:
                try:
                    # --- BRAND ---
                    brand_tag = prod.select_one("p[data-test-info-type='brandName']")
                    brand = brand_tag.text.strip() if brand_tag else "N/A"

                    # --- NAME ---
                    name_tag = prod.select_one("h3.card-title")
                    name = name_tag.text.strip() if name_tag else "N/A"

                    # --- PRICE (CLEAN) ---
                    price_tag = prod.select_one("div[data-test-info-type='price']")
                    if price_tag:
                        raw_price = price_tag.text.strip()
                        price = extract_first_price(raw_price)
                    else:
                        price = "N/A"

                    # --- OFFER ---
                    offer_tag_img = prod.select_one("div.shipping-message__search img[alt]")
                    offer_tag_div = prod.select_one("div.shipping-message__search")
                    if offer_tag_img:
                        offer = offer_tag_img["alt"].strip()
                    elif offer_tag_div:
                        offer = offer_tag_div.get_text(strip=True)
                    else:
                        offer = ""

                    # --- URL ---
                    link_tag = prod.select_one("h3.card-title a[href]")
                    if link_tag:
                        href = link_tag["href"].strip()
                        if href.startswith("http"):
                            link = href
                        elif href.startswith("/"):
                            link = "https://www.rockbottomgolf.com" + href
                        else:
                            link = "https://www.rockbottomgolf.com/" + href
                    else:
                        link = "N/A"

                    if not all([brand, name, price, link]):
                        print(f"⚠️ Skipped incomplete: {brand} | {name} | {price} | {link}")
                        continue

                    # ✅ Save final correct order: page, name, price, brand, link, offer
                    all_products.append([
                        page, name, price, brand, link, offer
                    ])

                    print(f"✅ {page}: {name} | {price} | {brand} | {link} | {offer}")

                except Exception as e:
                    print(f"⚠️ Error parsing product: {e}")
                    continue

    except Exception as e:
        print(f"❌ Error during scraping: {e}")

    return all_products
