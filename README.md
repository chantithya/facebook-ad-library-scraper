# Facebook Ad Library Scraper

## 📌 Project Overview
This project is a web scraper that collects advertisement data from the Facebook Ad Library.

## 🎯 Objective
- Search ads using keyword: "slot machine"
- Target country: Vietnam
- Extract competitor creative data

## 📊 Data Collected
- Status (Active / Inactive)
- Library ID
- Date Range
- Page Name
- Page Link
- Sponsored Label
- Ad Text (Caption)
- Image / Video URL
- Destination Link

## 🛠 Technologies Used
- Python
- Selenium
- Requests
- Pandas

## ▶️ How to Run

1. Install dependencies:
pip install -r requirements.txt


2. Run scraper:
python scraper.py


## 📁 Output
- `ads_full_data.csv`
- Media files saved in `/images`

## ⚠️ Notes
- Facebook Ad Library uses dynamic content (React)
- Scraper includes delay and error handling for stability

## 👨‍💻 Author
Som Chantithya
