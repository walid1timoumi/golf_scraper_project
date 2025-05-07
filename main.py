import sys
import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from services.email_sender import send_email
from services.google_sheets import upload_to_sheets
from analysis.analyzer import analyze_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import project modules
try:
    from scrapers.globalgolf_scraper import parse_globalgolf
    from scrapers.rockbottom_scraper import parse_rockbottom
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def load_config(site):
    config_path = project_root / "config" / f"{site}_config.json"
    try:
        with open(config_path) as f:
            content = f.read()
            if not content.strip():
                raise ValueError(f"Config file {config_path} is empty")
            return json.loads(content)
    except FileNotFoundError:
        print(f"❌ Config file not found at: {config_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_path}: {str(e)}")
        raise

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Use WebDriver Manager for automatic driver handling
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scrape_site(site_name):
    driver = create_driver()
    try:
        config = load_config(site_name)
        print(f"\n=== Starting {site_name} scrape ===")
        if site_name == "globalgolf":
            results = parse_globalgolf(driver, config)
        elif site_name == "rockbottom":
            results = parse_rockbottom(driver, config)
        else:
            results = []
        
        print(f"✅ {site_name} scraping complete. Products: {len(results) if results else 0}")
        return results
    except Exception as e:
        print(f"❌ Error scraping {site_name}: {str(e)}")
        return []
    finally:
        driver.quit()

def format_raw_data(products: list, source: str) -> list:
    formatted = []
    for product in products:
        if source == "globalgolf" and len(product) == 6:
            page, name, price, brand, url, offer = product
            formatted.append([source, page, name, price, brand, url, offer])
        elif source == "rockbottom" and len(product) == 6:
            page, name, price, brand, url, offer = product
            formatted.append([source, page, name, price, brand, url, offer])
        else:
            formatted.append([source] + product)
    return formatted

def main():
    try:
        sites_to_scrape = ["globalgolf", "rockbottom"]
        results = {}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(scrape_site, site): site for site in sites_to_scrape}
            
            for future in futures:
                site = futures[future]
                try:
                    results[site] = future.result()
                except Exception as e:
                    print(f"⚠️ Thread error for {site}: {e}")
                    results[site] = []

        # Debug output
        print("\n=== Scraping Results Summary ===")
        for site, products in results.items():
            print(f"{site}: {len(products)} products")
            if products and len(products) > 0:
                print(f"Sample product: {products[0]}")

        all_products = []
        for source, products in results.items():
            if products:
                all_products.extend(format_raw_data(products, source))

        if not all_products:
            raise ValueError("No products scraped from any site")

        # Run the advanced analyzer
        analysis = analyze_data(results)

        print("\n=== Scraping Completed Successfully ===")
        print(analysis["raw_data"].head(3))

        combined_data = {
            "raw_data": analysis["raw_data"],
            "stats": analysis["stats"],
            "top_brands": analysis["top_brands"],
            "best_deals": analysis["stats"].sort_values("Min_Price").head(10),
            "top_expensive": analysis["top_expensive"]
        }

        # Upload to Google Sheets
        if not upload_to_sheets(combined_data):
            raise RuntimeError("Failed to upload to Google Sheets")

        # Send email notification
        subject = "✅ Scraping Completed Successfully!"
        sheet_url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}"
        content = f"""✅ Golf clubs scraping finished successfully.
📊 Total products scraped: {len(all_products)}
📄 View Google Sheet: {sheet_url}"""
        
        send_email(subject, content)

    except Exception as e:
        print(f"⚠️ Critical Error: {str(e)}", file=sys.stderr)
        # Send error email if possible
        if os.getenv('TO_EMAIL'):
            send_email("❌ Scraper Failed", f"Error: {str(e)}")
        raise
    finally:
        print("✅ Scraping completed at", time.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()