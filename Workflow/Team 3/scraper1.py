#THIS TAKES A REALLY LONG TIME TO FETCH THE DATA SO ONLY RUN IT IF YOU ARE DETERMINED

import os
import datetime
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

from Workflow.scraper_utils import append_rows, make_job_row

sw_url = 'https://www.glassdoor.com/Job/chicago-il-us-software-developer-jobs-SRCH_IL.0,13_IC1128808_KO14,32.htm'
da_url = 'https://www.glassdoor.com/Job/chicago-il-data-analyst-jobs-SRCH_IL.0,10_IC1128808_KO11,23.htm'
ds_url = 'https://www.glassdoor.com/Job/chicago-il-data-scientist-jobs-SRCH_IL.0,10_IC1128808_KO11,25.htm'
dteng_url = 'https://www.glassdoor.com/Job/chicago-il-data-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,24.htm'
cloud_url = 'https://www.glassdoor.com/Job/chicago-il-cloud-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,25.htm'
dvop_url = 'https://www.glassdoor.com/Job/chicago-il-dev-ops-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,27.htm'
mleng_url = 'https://www.glassdoor.com/Job/chicago-il-machine-learning-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,36.htm'
web_url = 'https://www.glassdoor.com/Job/chicago-il-web-developer-jobs-SRCH_IL.0,10_IC1128808_KO11,24.htm'

url_list = [
    ("software developer", "Chicago, IL", sw_url),
    ("data scientist", "Chicago, IL", ds_url),
    ("data analyst", "Chicago, IL", da_url),
    ("dev ops engineer", "Chicago, IL", dvop_url),
    ("machine learning engineer", "Chicago, IL", mleng_url),
    ("cloud engineer", "Chicago, IL", cloud_url),
    ("web developer", "Chicago, IL", web_url),
    ("data engineer", "Chicago, IL", dteng_url),
]

def scrape_page(driver, seen_ids, search_term, search_location, source_url):
    page_rows = []

    job_column = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul[aria-label="Jobs List"]')))
    jobs = WebDriverWait(job_column, 3).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'li')))
    print(f'found {len(jobs)} job cards')

    added = 0

    for j in jobs:
        #print(j.text)
        job_id = j.id
        if job_id not in seen_ids:
            try:
                title = j.find_element(By.CSS_SELECTOR, '*[class*="jobTitle"]').text.strip()
                #print(title)
                location = j.find_element(By.CSS_SELECTOR, '*[class*="location"]').text.strip()
                #print(location)
                try:
                    salary = j.find_element(By.CSS_SELECTOR, '*[class*="salaryEstimate"]').text.strip()
                    #print(salary)
                except:
                    salary = ''
                    #print('[salary not reported]')
                description = j.find_element(By.CSS_SELECTOR, '*[class*="jobDescription"]').text.strip()
                #print(description)
            except:
                title = -1
        
            if title != -1:
                seen_ids.add(job_id)
                page_rows.append(
                    make_job_row(
                        source="glassdoor",
                        search_term=search_term,
                        search_location=search_location,
                        source_url=source_url,
                        title=title,
                        job_location=location,
                        salary=salary,
                        description=description,
                    )
                )
                added += 1
    
    print(f'{added} jobs appended out of {len(jobs)} found')
    return page_rows

def main():
    seen_ids = set()
    fileNm = f'GlassdoorPull-{datetime.date.today()}.csv'

    if os.path.exists(fileNm):
        write = input(f'{fileNm} already exists. Overwrite? (Y/N): ')
    else:
        write = 'y'

    print(f'Launching Chrome browser... write?: {write}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(1)

    try:
        for search_term, search_location, url in url_list:
            driver.get(url)
            page_rows = scrape_page(driver, seen_ids, search_term, search_location, url)
            append_rows(page_rows, fileNm)
            jobListing = len(page_rows)

            cont = 'y'
            while jobListing > 0 and cont.lower().startswith('y'):
                try:
                    buttonMore = driver.find_element(By.CSS_SELECTOR, 'button[data-test=load-more]')
                    if buttonMore:
                        ActionChains(driver).move_to_element(buttonMore).pause(2).click().perform()
                        ActionBuilder(driver).clear_actions()
                except Exception as e:
                    print(f"[Error] Load more: {e}")

                try:
                    buttonClose = driver.find_element(By.CSS_SELECTOR, '.CloseButton')
                    if buttonClose:
                        ActionChains(driver).move_to_element(buttonClose).pause(1).click().perform()
                        ActionBuilder(driver).clear_actions()
                        print('closed the popup')
                except:
                    print('no popup')

                driver.implicitly_wait(1)
                page_rows = scrape_page(driver, seen_ids, search_term, search_location, url)
                append_rows(page_rows, fileNm)
                jobListing = len(page_rows)

    except Exception as e:
        print(f"[CRASH] Something went wrong: {e}")
        print("Saving progress before exiting...")

    finally:
        driver.quit()
        print("Driver closed.")



if __name__ == "__main__":
    main()
