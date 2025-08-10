from selenium import webdriver
from scraper import scrape_all_members

if __name__ == "__main__":
    driver = webdriver.Chrome()
    try:
        data = scrape_all_members(driver)
        print(data)
        # Save or process `data`
    finally:
        driver.quit()
