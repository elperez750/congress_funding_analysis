from helpers.data_cleaners import parse_currency_string
from helpers.parsers import scrape_member_page
from bs4 import BeautifulSoup


# This is where we will be implementing pagination


def scrape_all_members(driver):
    congress_information = []

    driver.get('https://www.opensecrets.org/members-of-congress/members-list?cong_no=118&cycle=2024&sort=N')
    html_content = driver.page_source

    # This will get the page with all of the basic information
    soup = BeautifulSoup(html_content, 'html.parser')


    # Table with all representatives
    table_body = soup.find('tbody')

    congress_people_basic_info = None
    # # Getting all the rows with the congress people info including names party, and some financials for example
    for row in table_body:
        congress_people_basic_info = soup.find_all('tr')

    print(congress_people_basic_info[1:-1])

    base_url = 'https://www.opensecrets.org'
    for entry in congress_people_basic_info[1:-1]:
        member_information = {}
        row = entry.find_all('td')
        link = entry.find_all('a')[0]['href']

        full_link = base_url + link


        member_information['link'] = full_link
        member_information['name'] = row[0].find('a').text.strip()
        member_information['state'] = row[1].text
        member_information['chamber'] = row[2].text
        member_information['party'] = row[3].text
        member_information['raised'] = parse_currency_string(row[4].text)
        member_information['spent'] = parse_currency_string(row[5].text)
        member_information['cash_on_hand'] = parse_currency_string(row[6].text)
        member_information['debts'] = parse_currency_string(row[7].text)

        scrape_member_page(driver,
full_link)


        congress_information.append(member_information)
