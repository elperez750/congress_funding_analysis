# creating a function that will in charge of scraping from the other page
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from helpers.data_cleaners import *
from scraper import member_information
import time

def get_contributor_data(driver):
    total_vs_avg_list = []

    # This will get the plot group dynamically (any number instead of hardcoding 81)
    chart_for_earned = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'raphael-group-') and contains(@class,'plot-group')]"))
    )

    # Grab all the bars inside the plot
    bar_elements = chart_for_earned.find_elements(By.TAG_NAME, 'rect')
    actions = ActionChains(driver)

    for bar in bar_elements:
        try:
            # Hover over each bar
            actions.move_to_element(bar).perform()

            # Wait for the tooltip to be visible
            tooltip_el = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "fc__tooltip"))
            )

            # Get only the tooltip's HTML
            tooltip_html = tooltip_el.get_attribute("outerHTML")

            # Parse just the tooltip
            tooltip_soup = BeautifulSoup(tooltip_html, "html.parser")
            data_divs = tooltip_soup.find_all("div")
            if not data_divs or len(data_divs) < 4:
                continue

            # Extract and clean the data


            year = convert_two_digit_year(data_divs[3].text.split(',')[1])
            total_raised_by_member = parse_abbreviated_number(data_divs[3].text.split(',')[2])
            average_raised_by_member = parse_abbreviated_number(data_divs[0].text.split(',')[-1])

            total_vs_avg_list.append({
                'year': year,
                'total_raised_by_congressman': total_raised_by_member,
                'average_raised': average_raised_by_member
            })

        except Exception as e:
            print("Tooltip did not appear:", e)
            continue

    return total_vs_avg_list

'''
This is responsible for getting the first and last election if applicable.

Sometimes the final entry is next election or about to retire. For that we call the column election type
'''
def get_election_details(individual_soup):

    election_dates = individual_soup.find_all('div', class_="Congress--profile-timeline-item")
    election_object = {
        'first_election': None,
        'election_type': None,
        'election_year': None
    }


    for item in election_dates:
        date = item.select_one('.Congress--profile-timeline-date')
        label = item.select_one('.Congress--profile-timeline-label')

        date_text = date.get_text(strip=True) if date else None
        label_text = label.get_text(strip=True)

        if not label_text:
            continue

        if label_text == 'First Election':
            election_object['first_election'] = date_text

        elif label_text in ["Last Election", "Next Election", "Retiring at session end"]:
            election_object["election_type"] = label_text
            election_object["election_year"] = date_text if date_text and re.fullmatch(r"\d{4}",date_text) else None

    return election_object


'''
This will basically give us the names and amounts of the top industries and contributors for this member
'''
def set_top_industry_and_contributor(individual_soup):

    # This will basically give us all the numbers
    top_industries_contributors_numbers = individual_soup.find_all('div',
                                                                   class_="Congress--profile-top-numbers--info--stats-number")

    # This will give us the names
    top_industries_contributor_names = individual_soup.find_all('div',
                                                                class_="Congress--profile-top-numbers--info--stats-name")

    member_information[20]['top_industry'] = top_industries_contributor_names[0].text
    member_information[20]['top_contributor'] = top_industries_contributor_names[1].text

    # Getting the numbers for the industry and contributor
    member_information[20]['top_industry_number'] = parse_currency_string(top_industries_contributors_numbers[0].text)
    member_information[20]['top_contributor_number'] = parse_currency_string(top_industries_contributors_numbers[1].text)



def set_all_contributors_and_industries(individual_soup):
    top_contributors_list = []
    top_industries_list = []
    tables_for_individual_page = individual_soup.find_all('table', class_="js-scrollable")

    contributor_table = tables_for_individual_page[0]
    industries_table = tables_for_individual_page[1]

    for tr in contributor_table.find_all('tr'):
        top_contributors_object = {}
        contributor_row = tr.find_all('td')
        if not contributor_row:
            continue

        top_contributors_object['Contributor'] = contributor_row[0].text
        top_contributors_object['total'] = contributor_row[1].text
        top_contributors_object['individuals'] = contributor_row[2].text
        top_contributors_object['pacs'] = contributor_row[3].text

        top_contributors_list.append(top_contributors_object)

    member_information[2]['top_contributors'] = top_contributors_list

    for tr in industries_table.find_all('tr'):

        top_industries_object = {}

        industry_row = tr.find_all('td')

        if not industry_row:
            continue

        top_industries_object['industry'] = industry_row[0].text
        top_industries_object['total'] = industry_row[1].text
        top_industries_object['individuals'] = industry_row[2].text
        top_industries_object['pacs'] = industry_row[3].text

        top_industries_list.append(top_industries_object)

        # The index will be changed dynamically soon
    member_information[2]['top_industries'] = top_industries_list

def set_contributions(individual_soup):
    table_for_contributions = individual_soup.find_all('div', class_="HorizontalStackedBar")

    all_contribution_data = []
    for div_element in table_for_contributions:

        trs_in_div = div_element.find_all('tr')
        for td in trs_in_div:
            contribution_data = {}
            cells = td.find_all('td')

            contribution_type = cells[0].text
            contribution_amount = cells[1].text
            contribution_percent = cells[2].text

            contribution_data['contribution_type'] = clean_key(contribution_type)
            contribution_data['contribution_amount'] = parse_currency_string(contribution_amount.strip())
            contribution_data['contribution_percent'] = int(float(contribution_percent.strip().strip('%')))

            all_contribution_data.append(contribution_data)

        member_information[2]['all_contribution_data'] = all_contribution_data



def scrape_individual_page(driver, link_congressman):

    # This is responsible for getting us to the individual member page
    driver.get("about:blank")  # Clear any existing state
    driver.get(link_congressman)
    page_title = driver.title
    individual_page_src = driver.page_source
    individual_soup = BeautifulSoup(individual_page_src, 'html.parser')



    member_information[2]['raised_by_year'] = get_contributor_data(driver)
    election_info = get_election_details(individual_soup)
    member_information[2].update(election_info)


    set_top_industry_and_contributor(individual_soup)
    set_all_contributors_and_industries(individual_soup)
    set_contributions(individual_soup)






print(scrape_individual_page(member_information[2]['link']))
print(member_information[2])