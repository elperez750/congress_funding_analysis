# creating a function that will in charge of scraping from the other page
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from helpers.data_cleaners import *
from scraper import member_information
import re


def parse_raised_by_year(driver):
    total_vs_avg_obj = {
        'total_vs_avg_raised': []
    }

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

            total_vs_avg_obj['total_vs_avg_raised'].append({
                'year': year,
                'total_raised_by_congressman': total_raised_by_member,
                'average_raised': average_raised_by_member
            })

        except Exception as e:
            print("Tooltip did not appear:", e)
            continue

    return total_vs_avg_obj

'''
This is responsible for getting the first and last election if applicable.

Sometimes the final entry is next election or about to retire. For that we call the column election type
'''
def parse_election_details(individual_soup):
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
def parse_top_ic(individual_soup):
    top_ic_data = {
        'top_industry': None,
        'top_contributor': None,
        'top_industry_number': None,
        'top_contributor_number': None,
    }

    # This will basically give us all the numbers
    top_industries_contributors_numbers = individual_soup.find_all('div',
                                                                   class_="Congress--profile-top-numbers--info--stats-number")

    # This will give us the names
    top_industries_contributor_names = individual_soup.find_all('div',
                                                                class_="Congress--profile-top-numbers--info--stats-name")


    top_ic_data['top_industry'] = top_industries_contributor_names[0].text
    top_ic_data['top_contributor'] = top_industries_contributor_names[1].text


    top_ic_data['top_industry_number'] = top_industries_contributors_numbers[0].text
    top_ic_data['top_contributor_number'] = top_industries_contributors_numbers[1].text

    return top_ic_data



def parse_ic_tables(individual_soup):

    # This will contain the contributors and industries list for the member
    all_ic_obj = {
        "all_industries": [],
        "all_contributors": [],
    }

    tables_for_individual_page = individual_soup.find_all('table', class_="js-scrollable")

    contributor_table = tables_for_individual_page[0]
    industries_table = tables_for_individual_page[1]

    for tr in contributor_table.find_all('tr'):
        top_contributors_object = {}
        contributor_row = tr.find_all('td')
        if not contributor_row:
            continue

        top_contributors_object['contributor'] = contributor_row[0].text
        top_contributors_object['total'] = contributor_row[1].text
        top_contributors_object['individuals'] = contributor_row[2].text
        top_contributors_object['pacs'] = contributor_row[3].text

        all_ic_obj['all_contributors'].append(top_contributors_object)


    for tr in industries_table.find_all('tr'):

        top_industries_object = {}

        industry_row = tr.find_all('td')

        if not industry_row:
            continue

        top_industries_object['industry'] = industry_row[0].text
        top_industries_object['total'] = industry_row[1].text
        top_industries_object['individuals'] = industry_row[2].text
        top_industries_object['pacs'] = industry_row[3].text

        all_ic_obj['all_industries'].append(top_industries_object)

    return all_ic_obj


def parse_sources_of_funds(individual_soup):
    table_for_contributions = individual_soup.find_all('div', class_="HorizontalStackedBar")
    source_of_funds_obj = {
        'funding_type': []
    }

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

            source_of_funds_obj['funding_type'].append(contribution_data)


    return source_of_funds_obj






def scrape_member_page(driver, link_congressman):
    # This is responsible for getting us to the individual member page
    driver.get("about:blank")  # Clear any existing state
    driver.get(link_congressman)
    individual_page_src = driver.page_source
    individual_soup = BeautifulSoup(individual_page_src, 'html.parser')


    top_ic_data = parse_top_ic(individual_soup)
    all_ic_data = parse_ic_tables(individual_soup)
    all_funding = parse_sources_of_funds(individual_soup)
    election_info = parse_election_details(individual_soup)
    raised_by_year = parse_raised_by_year(driver)
    
    
    member = {}
    member.update(top_ic_data)
    member.update(all_ic_data)
    member.update(all_funding)
    member.update(raised_by_year)
    member.update(election_info)


    return member









