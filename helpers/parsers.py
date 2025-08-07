# creating a function that will in charge of scraping from the other page
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from helpers.data_cleaners import *
import time


def scrape_individual_page(driver, link_congressman):

    top_contributors_list = []
    top_industries_list = []
    total_vs_avg_list = []
    sources_of_funds = []

    # This is responsible for getting us to the individual member page
    driver.get("about:blank")  # Clear any existing state
    driver.get(link_congressman)
    page_title = driver.title
    individual_page_src = driver.page_source
    individual_soup = BeautifulSoup(individual_page_src, 'html.parser')


    election_dates = individual_soup.find_all('div', class_="Congress--profile-timeline-date")



    chart_for_earned = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'raphael-group-81-plot-group'))
        )





    bar_elements = chart_for_earned.find_elements(By.TAG_NAME, 'rect')

    print(len(bar_elements))
    actions = ActionChains(driver)


    for bar in bar_elements:
        print("THis is a bar", bar)
        actions.move_to_element(bar).perform()
        try:
            # Wait for tooltip to appear
            average_vs_total_object = {}

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "fc__tooltip"))
            )

            # Now get the updated HTML
            bar_soup = BeautifulSoup(driver.page_source, 'html.parser')
            tooltip_div = bar_soup.find('div', class_="fc__tooltip fusioncharts-div")

            print(tooltip_div)

            if tooltip_div:
                data_divs = tooltip_div.find_all('div')
                if not data_divs:
                    continue




                #print("Here are the data divs", data_divs)
                #print(data_divs[3].text.split(',')[1])
                year = convert_two_digit_year(data_divs[3].text.split(',')[1])

                total_raised_by_congressman = parse_abbreviated_number(data_divs[0].text.split(',')[2])
                average_raised = parse_abbreviated_number(data_divs[3].text.split(',')[2])


                #print(year)
                #print(average_raised)
                #print(total_raised_by_congressman)

                average_vs_total_object['year'] = year
                average_vs_total_object['total_raised_by_congressman'] = total_raised_by_congressman
                average_vs_total_object['average_raised'] = average_raised


                total_vs_avg_list.append(average_vs_total_object)
        except Exception as e:
            print("Tooltip did not appear:", e)
            continue




    # these will be switched once we loop through all of the links
    congress_information[2]['first_election'] = election_dates[0].text
    congress_information[2]['upcoming_election'] = election_dates[1].text

    top_industries_contributors_numbers = individual_soup.find_all('div', class_="Congress--profile-top-numbers--info--stats-number")
    top_industries_contributor_names = individual_soup.find_all('div', class_="Congress--profile-top-numbers--info--stats-name")

    # This will have to be cleaned up to remove dollar sign and commas
    congress_information[2]['top_industry'] = top_industries_contributor_names[0].text
    congress_information[2]['top_contributor'] = top_industries_contributor_names[1].text

    # Getting the numbers for the industry and contributor
    congress_information[2]['top_industry_number'] = top_industries_contributors_numbers[0].text
    congress_information[2]['top_contributor_number'] = top_industries_contributors_numbers[1].text


    tables_for_individual_page = individual_soup.find_all('table', class_="js-scrollable")


    contributor_table = tables_for_individual_page[0]
    industries_table = tables_for_individual_page[1]
    # Total vs average raised

    # {year: 12, raised_by_congressman: 1.23, average_raised: 2.44 }

    # If year < 24 and <= 00

    # This will get everything in the contributors table
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
        congress_information[2]['top_contributors'] = top_contributors_list
        congress_information[2]['total_vs_avg'] = total_vs_avg_list



    # This will get everything in the industries table
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
        congress_information[2]['top_industries'] = top_industries_list


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


        congress_information[2]['all_contribution_data'] = all_contribution_data













# Class name for hoverables
# fc__tooltip fusioncharts-div
    return page_title
print(scrape_individual_page(congress_information[2]['link']))
print(congress_information[2])