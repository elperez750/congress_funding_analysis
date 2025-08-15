# Congressional Fundraising Data Engineering Project

## 📌 Overview
This project scrapes, cleans, and analyzes fundraising data for **all U.S. House and Senate members (2023–2024)** from [OpenSecrets.org](https://www.opensecrets.org).  
It demonstrates **data engineering skills** across web scraping, data cleaning, transformation, and basic political finance analysis.

The repository includes:
- A **scraper** (`main.py`) built with **Selenium** and **Beautiful Soup**.
- Helper functions in **`data_cleaners.py`** (data cleaning utilities) and **`parsers.py`** (HTML parsing functions).
- A **processed CSV** of fundraising data for instant analysis.
- Example analysis scripts answering core political finance questions.


---

## ⚙️ Tech Stack
- **Python** → data extraction, cleaning, transformation
- **Pandas** → tabular processing and aggregation
- **Selenium** → automated browser interaction (e.g., page navigation, hover actions)
- **Beautiful Soup** → HTML parsing and data extraction
- **Jupyter Notebooks** → exploratory analysis

---

## 🚀 How to Use

### Option 1 — Use the prepared dataset (fastest)
Simply open one of the notebooks in the `notebooks/` folder and run the analysis directly on `congress_members_2024.csv`.



### Option 2 — Scrape fresh data by running main.py

---

## 🛠️ Data Pipeline Steps

### 1. Data Ingestion
- **Source**: OpenSecrets.org congressional fundraising pages (2023–2024).
- **House & Senate**: Both chambers scraped in one run.
- **Pagination**: Automated movement to subsequent pages to scrape all members.

### 2. Scraping Tools & Methods
- **Selenium**:
  - Navigates between pages.
  - Handles interactive elements like hovering over bars to reveal data.
- **Beautiful Soup**:
  - Parses static and dynamically loaded HTML tables.
  - Extracts relevant fundraising and contributor data.

### 3. Data Cleaning
- Standardized column names and formats.
- Converted monetary values to integers for calculations.
- Normalized contributor and industry names.
- Implemented checks for missing or empty tables per member.

### 4. Data Storage
- Saved as `congress_fundraising_2023_2024.csv`.
- CSV format allows easy import into databases or further analysis tools.

### 5. Analysis & Insights
The dataset was used to answer:
- Total fundraising by **Senate** vs **House** members.
- Top industries per **state**.
- Top industries per **state** for each **party**.
- States that raise the most money overall.
- Industries contributing the most nationwide.
- Top industries for **Senators** and **House members**.
- Average increase in money raised per candidate over time.

---

## 📂 Project Structure
```plaintext
congress-funding-analysis/
│
├── helpers/
│   ├── data_cleaners.py        # Utility functions for cleaning scraped data
│   ├── parsers.py              # HTML parsing functions
│
├── notebooks/
│   ├── 01_data_exploration.ipynb # Initial exploration & cleaning
│   ├── 02_data_exploration.ipynb # Further analysis & visualizations
│
├── .gitignore
├── congress_members_2024.csv   # Processed dataset (ready-to-use)
├── main.py                     # Full scraper pipeline
├── scraper.py                  # Scraping logic separated for modularity
├── README.md
├── requirements.txt            # Python dependencies
└── venv/                       # Virtual environment (not tracked in Git)
