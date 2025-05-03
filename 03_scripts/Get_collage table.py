# 03_scripts/dynamic_scraper_nirf.py

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_table(driver, url):
    driver.get(url)
    print(f"🌐 Opening {url}")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        print("✅ Table located, extracting data...")
    except Exception as e:
        print("❌ Table not found:", e)
        return None

    tables = pd.read_html(driver.page_source)
    if len(tables) > 0:
        return tables[0]
    else:
        print("❌ No tables extracted.")
        return None

def save_data(df, filename):
    os.makedirs("01_raw_data", exist_ok=True)
    filepath = os.path.join("01_raw_data", filename)
    df.to_excel(filepath, index=False)
    print(f"✅ Data saved at {filepath}")

def main():
    urls = {
        "Engineering": "https://www.nirfindia.org/Rankings/2024/EngineeringRanking.html",
        "Management": "https://www.nirfindia.org/Rankings/2024/ManagementRanking.html",
        "Pharmacy": "https://www.nirfindia.org/Rankings/2024/PharmacyRanking.html",
        "University": "https://www.nirfindia.org/Rankings/2024/UniversityRanking.html",
    }

    driver = init_driver(headless=False)  # set headless=True if no need to see browser

    for category, url in urls.items():
        print(f"\n🔵 Scraping {category} ranking...")
        try:
            df = scrape_table(driver, url)
            if df is not None:
                save_data(df, f"nirf_{category.lower()}_2023.xlsx")
            else:
                print(f"⚠️ No data extracted for {category}.")
        except Exception as e:
            print(f"❌ Error scraping {category}: {e}")
    
    driver.quit()
    print("\n🎯 Scraping completed for all categories.")

if __name__ == "__main__":
    main()
