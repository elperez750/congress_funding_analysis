#url = 'https://www.opensecrets.org/members-of-congress/members-list?cong_no=118&cycle=2024&sort=N'
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service)


driver.get('https://www.opensecrets.org/members-of-congress/members-list?cong_no=118&cycle=2024&sort=N')
print('Page title', driver.title)
html_content = driver.page_source


# This will get the page with all of the basic information
soup = BeautifulSoup(html_content, 'html.parser')

# Table with all representatives
table_body = soup.find('tbody')


# # Getting all the rows with the congress people info including names party, and some financials for example
for row in table_body:
    congress_people_basic_info = soup.find_all('tr')


print(congress_people_basic_info[1:-1])



driver.close()
driver.quit()


