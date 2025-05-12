# 🏌️ Golf Club Price Scraper (GlobalGolf & RockBottomGolf)

This project automatically scrapes golf club listings from two major retailers — **GlobalGolf** and **RockBottomGolf** — and analyzes the data for trends, brand stats, and best deals. It runs on a fully automated pipeline using **Python + Selenium + GitHub Actions**, with outputs stored in **Google Sheets**, and optional email reporting.

---

## 📊 Features

- ✅ Real-time scraping from:
  - 🔹 [globalgolf.com](https://www.globalgolf.com)
  - 🔹 [rockbottomgolf.com](https://www.rockbottomgolf.com)
- ✅ Handles pagination, popups, and dynamic JS content
- ✅ Extracts: product name, price, brand, URL, and promotional offer
- ✅ Analyzes data: average/min/max prices by brand
- ✅ Outputs to multi-tab Google Sheet
- ✅ Sends summary via email (SendGrid)
- ✅ Fully automated using GitHub Actions (every 3 days)

---

## 🎥 Demo Video

[![Watch the demo](https://img.youtube.com/vi/8FsjIRTiMZM/0.jpg)](https://youtu.be/8FsjIRTiMZM)

> 📽️ See the full automation pipeline in action — scraping golf listings, analyzing them, exporting to Google Sheets, and sending email reports.


---

## 📁 Project Structure

```
.
├── main.py                    # Main controller
├── scrapers/
│   ├── globalgolf_scraper.py
│   └── rockbottom_scraper.py
├── analysis/
│   └── analyzer.py
├── services/
│   ├── email_sender.py
│   └── google_sheets.py
├── config/
│   └── {site}_config.json
└── .github/workflows/
    └── run_scraper.yml
```

---

## 📦 Sample Data Fields

| Field    | Example                                 |
|----------|-----------------------------------------|
| Name     | TaylorMade SIM2 Max Driver              |
| Price    | $279.99                                 |
| Brand    | TaylorMade                              |
| URL      | https://www.globalgolf.com/product/...  |
| Offer    | Free Shipping / Deal badge              |

---

## 📈 Google Sheets Output

Results are published in a Google Sheet with the following tabs:

- **Raw Data** – complete scraped listings
- **Stats** – avg/min/max price by brand
- **Top Brands** – most frequent brands
- **Best Deals** – lowest price listings
- **Top Expensive** – highest price listings

---

## 🚀 Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/golf-scraper.git
cd golf-scraper
pip install -r requirements.txt

# Add credentials and environment values
cp .env.example .env

# Run
python main.py
```

---

## ⚙️ GitHub Automation

This project runs automatically on GitHub Actions:

- Scrapes fresh listings every 3 days
- Pushes data to Google Sheets
- Sends summary email

To trigger manually, use the "Run workflow" button on GitHub.

---

## ✉️ Email Reporting

Configure via GitHub secrets:
- `SENDGRID_API_KEY`
- `FROM_EMAIL`
- `TO_EMAIL`

---

## 💡 Tech Stack

- Python, Selenium, BeautifulSoup
- gspread (Google Sheets API)
- Pandas for analysis
- GitHub Actions (CI/CD)
- SendGrid (email notifications)

---

## 👤 Author

### Walid Timoumi  
Sourcing Specialist & Automation Developer  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://linkedin.com/in/your-link)  
[![Upwork](https://img.shields.io/badge/Upwork-Freelancer-success?logo=upwork)](https://www.upwork.com/freelancers/your-link)

---

> 🤖 Built with ❤️ by Walid — Automated, analyzed, and production-ready.
