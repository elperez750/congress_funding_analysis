from helpers.data_cleaners import parse_currency_string
from helpers.parsers import scrape_member_page
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def scrape_all_members(driver):
    congress_information = []

    driver.get('https://www.opensecrets.org/members-of-congress/members-list?cong_no=118&cycle=2024&sort=N')

    base_url = 'https://www.opensecrets.org'

    while True:
        try:
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            table_body = soup.find('tbody')
            congress_people_basic_info = table_body.find_all('tr')

            for entry in congress_people_basic_info:
                try:
                    member_information = {}
                    row = entry.find_all('td')

                    if len(row) < 8:
                        print(f"Skipping row with only {len(row)} columns")
                        continue

                    links = entry.find_all('a')
                    if not links:
                        print("Skipping row with no links")
                        continue

                    link = links[0]['href']
                    full_link = base_url + link
                except Exception as member_error:
                    print('Error in scrape_all_members: ', member_error)
                    continue

                member_information['link'] = full_link
                member_information['name'] = row[0].find('a').text.strip() if row[0].find('a') else 'Unknown'
                member_information['state'] = row[1].text
                member_information['chamber'] = row[2].text
                member_information['party'] = row[3].text
                member_information['raised'] = parse_currency_string(row[4].text)
                member_information['spent'] = parse_currency_string(row[5].text)
                member_information['cash_on_hand'] = parse_currency_string(row[6].text)
                member_information['debts'] = parse_currency_string(row[7].text)
                individual_page_details = scrape_member_page(driver, full_link)
                member_information.update(individual_page_details)

                congress_information.append(member_information)

            # After processing all members on the page, add this debugging:
            print(f"Finished processing {len(congress_people_basic_info)} members on current page")
            print(f"Total members scraped so far: {len(congress_information)}")

            # Debug the pagination buttons
            try:
                # Look for ALL pagination elements first
                all_pagination = driver.find_elements(By.CSS_SELECTOR, "a.paginate_button")
                print(f"Found {len(all_pagination)} pagination buttons")

                for i, button in enumerate(all_pagination):
                    print(f"Button {i}: class='{button.get_attribute('class')}', text='{button.text}'")

                # Now try to find the specific next button
                next_button = driver.find_element(By.CSS_SELECTOR, "a.paginate_button.next")
                print(f"Next button found: class='{next_button.get_attribute('class')}', text='{next_button.text}'")

                if "disabled" in next_button.get_attribute("class"):
                    print("Next button is disabled - reached last page")
                    break
                else:
                    print("Clicking next button...")
                    driver.execute_script("arguments[0].click();", next_button)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "tbody"))
                    )

            except Exception as pagination_error:
                print(f"Pagination error: {pagination_error}")

                # Let's see what pagination elements actually exist
                try:
                    all_links = driver.find_elements(By.CSS_SELECTOR, "a")
                    pagination_links = [link for link in all_links if "paginate" in link.get_attribute("class")]
                    print(f"Found {len(pagination_links)} links with 'paginate' in class")
                    for link in pagination_links:
                        print(f"  - {link.get_attribute('class')} : {link.text}")
                except:
                    print("Could not find any pagination elements")

                break

        except (KeyError, ValueError, IndexError) as e:
            print(f"Error: {e}")
            break

    # df = pd.DataFrame(congress_information)
    # df.to_csv('congress_members_2024.csv', index=False)
    # print(f"Saved {len(df)} congress members to CSV")

    return df
