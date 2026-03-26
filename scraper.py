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





# Create image folder
if not os.path.exists("images"):
    os.makedirs("images")

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Facebook Ad Library search URL
url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=VN&q=slot%20machine&search_type=keyword_unordered"

driver.get(url)

# Wait page load
time.sleep(10)

# Scroll page to load more ads
for i in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

# -------------------------
# SCRAPE
# -------------------------
# Wait until ads load
# -------------------------
# WAIT FOR DATA
# -------------------------
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Library ID')]"))
)

data = []
seen_ids = set()
count = 0

# Each ad = container around Library ID
# ads = driver.find_elements(By.XPATH, "//span[contains(text(),'Library ID')]/ancestor::div[5]")
# ads = driver.find_elements(By.XPATH, "//span[contains(text(),'Library ID')]/ancestor::div[8]")

# print("Ads found:", len(ads))


# ads = driver.find_elements(By.XPATH, "//span[contains(text(),'Library ID')]")
ads = driver.find_elements(
    By.XPATH,
    "//span[contains(text(),'Library ID')]/ancestor::div[@class='xh8yej3']"
)

# for i in range(len(ads)):
#     try:
#         ads = driver.find_elements(By.XPATH, "//span[contains(text(),'Library ID')]")
#         ad = ads[i]
#     except:
#         pass

for ad in ads:
    try:
        # -------------------------
        # LIBRARY ID (anchor)
        # -------------------------
        library_text = ad.find_element(
            By.XPATH, ".//span[contains(text(),'Library ID')]"
        ).text

        library_id = library_text.replace("Library ID:", "").strip()

        if library_id in seen_ids:
            continue
        seen_ids.add(library_id)

        # -------------------------
        # STATUS
        # -------------------------
        try:
            status = ad.find_element(By.XPATH, ".//span[text()='Active' or text()='Inactive']").text
        except:
            status = ""

        # -------------------------
        # DATE
        # -------------------------
        try:
            date = ad.find_element(By.XPATH, ".//span[contains(text(),'-')]").text
        except:
            date = ""

        # -------------------------
        # PAGE LINK
        # -------------------------
        page_link = ""
        try:
            page_link = ad.find_element(By.XPATH, ".//a[contains(@href,'facebook.com')]").get_attribute("href")
        except:
            pass

        # -------------------------
        # PAGE NAME (BEST FIX)
        # -------------------------
        try:
            page_name = ad.find_element(
                By.XPATH,
                ".//a[contains(@href,'facebook.com')]//span"
            ).text
        except:
            page_name = ""

        # -------------------------
        # SPONSORED
        # -------------------------
        sponsored = "No"
        try:
            ad.find_element(By.XPATH, ".//strong[text()='Sponsored']")
            sponsored = "Yes"
        except:
            pass

        # -------------------------
        # AD TEXT (VERY IMPORTANT FIX)
        # -------------------------
        try:
            ad_text = ad.find_element(
                By.XPATH,
                ".//div[contains(@style,'white-space: pre-wrap')]"
            ).text
        except:
            ad_text = ""

        # -------------------------
        # IMAGE (MAIN CREATIVE)
        # -------------------------
        image_url = ""
        try:
            link = ad.find_element(By.XPATH, ".//a[contains(@class,'x1lliihq')]")

            parent = link.find_element(By.XPATH, "./ancestor::div[3]")

            img = parent.find_element(By.XPATH, ".//img[contains(@src,'scontent')]")

            image_url = img.get_attribute("src")

        except:
            pass

        media_url = ""
        try:
            # 🎥 VIDEO FIRST
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

        destination_link = ""
        try:
            link = ad.find_element(
                By.XPATH,
                ".//a[contains(@class,'x1lliihq')]"
            )
            destination_link = link.get_attribute("href")
        except:
            pass

        # -------------------------
        # SAVE
        # -------------------------
        data.append({
            "status": status,
            "library_id": library_id,
            "date": date,
            "page_name": page_name,
            "page_link": page_link,
            "sponsored": sponsored,
            "ad_text": ad_text,
            'media_url': media_url
        })

        print(f"✅ {library_id} | {page_name}")

    except Exception as e:
        print("Error:", e)

# -------------------------
# SAVE CSV
# -------------------------
df = pd.DataFrame(data)
df.to_csv("ads_full_data.csv", index=False)

print("✅ Saved ads_full_data.csv")



# # Find images
# images = driver.find_elements(By.TAG_NAME, "img")

# print(f"Found {len(images)} images")

# count = 0

# for img in images:
#     src = img.get_attribute("src")

#     if src and "scontent" in src:

#         try:
#             response = requests.get(src)

#             filename = f"images/ad_{count}.jpg"

#             with open(filename, "wb") as f:
#                 f.write(response.content)

#             print("Saved:", filename)

#             count += 1

#         except:
#             pass