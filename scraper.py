from main import congress_people_basic_info
from helpers.data_cleaners import parse_currency_string
from helpers.parsers import scrape_individual_page



# This is where we will be implementing pagination
congress_information = []
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

    scrape_individual_page(full_link)


    congress_information.append(member_information)
