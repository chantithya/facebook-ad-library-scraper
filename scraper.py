import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from urllib.parse import quote






# Create image folder
if not os.path.exists("images"):
    os.makedirs("images")

if not os.path.exists("data"):
    os.makedirs("data")

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Facebook Ad Library search URL
# url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=VN&q=slot%20machine&search_type=keyword_unordered"

# keywords = ["slot machine"]
# keywords = ["slot machine", "online casino", "jackpot", "casino game", "Hi88",]

keywords = ["slot machine", "online casino", "jackpot", "casino game", "Hi88"]

for keyword in keywords:
    data = []   # reset per keyword
    seen_ids = set()

    encoded_keyword = quote(keyword)
    url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=VN&q={encoded_keyword}&search_type=keyword_unordered"

    print(f"🔍 Searching: {keyword}")
    driver.get(url)

    time.sleep(10)

    # Scroll
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Library ID')]"))
    )

    ads = driver.find_elements(
        By.XPATH,
        "//span[contains(text(),'Library ID')]/ancestor::div[@class='xh8yej3']"
    )

    # ✅ LOOP INSIDE KEYWORD
    for ad in ads:
        try:
            library_text = ad.find_element(
                By.XPATH, ".//span[contains(text(),'Library ID')]"
            ).text

            library_id = library_text.replace("Library ID:", "").strip()

            if library_id in seen_ids:
                continue
            seen_ids.add(library_id)

            # STATUS
            try:
                status = ad.find_element(By.XPATH, ".//span[text()='Active' or text()='Inactive']").text
            except:
                status = ""

            # DATE
            try:
                date = ad.find_element(By.XPATH, ".//span[contains(text(),'-')]").text
            except:
                date = ""

            # PAGE LINK + NAME
            page_link = ""
            page_name = ""
            try:
                link_el = ad.find_element(By.XPATH, ".//a[contains(@href,'facebook.com')]")
                page_link = link_el.get_attribute("href")
                page_name = link_el.text
            except:
                pass

            # SPONSORED
            sponsored = "No"
            try:
                ad.find_element(By.XPATH, ".//strong[text()='Sponsored']")
                sponsored = "Yes"
            except:
                pass

            # AD TEXT
            try:
                ad_text = ad.find_element(
                    By.XPATH,
                    ".//div[contains(@style,'white-space: pre-wrap')]"
                ).text
            except:
                ad_text = ""

            # MEDIA
            media_url = ""
            try:
                video = ad.find_elements(By.XPATH, ".//video")
                if video:
                    media_url = video[0].get_attribute("src")
                else:
                    images = ad.find_elements(By.XPATH, ".//img[contains(@src,'scontent')]")
                    for img in images:
                        src = img.get_attribute("src")
                        if src and "s60x60" not in src:
                            media_url = src
                            break
            except:
                pass

            # -------------------------
            # SAVE IMAGE
            # -------------------------
            folder_name = keyword.replace(" ", "_")
            folder_path = os.path.join("images", folder_name)

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            if media_url:
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(media_url, headers=headers, timeout=10)

                    if response.status_code == 200:
                        image_path = os.path.join(folder_path, f"{library_id}.jpg")
                        with open(image_path, "wb") as f:
                            f.write(response.content)
                except Exception as e:
                    print("Image download error:", e)

            # SAVE DATA
            data.append({
                "keyword": keyword,   # ✅ IMPORTANT (add keyword column)
                "status": status,
                "library_id": library_id,
                "date": date,
                "page_name": page_name,
                "page_link": page_link,
                "sponsored": sponsored,
                "ad_text": ad_text,
                "media_url": media_url
            })

            print(f"✅ {keyword} | {library_id} | {page_name}")

        except Exception as e:
            print("Error:", e)

    # -------------------------
    # SAVE CSV PER KEYWORD
    # -------------------------
    file_keyword = keyword.replace(" ", "_")
    csv_path = f"data/ads_full_data_{file_keyword}.csv"

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

    print(f"✅ Saved {csv_path}")