#THIS TAKES A REALLY LONG TIME TO FETCH THE DATA SO ONLY RUN IT IF YOU ARE DETERMINED

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
from pathlib import Path
import pandas as pd
import datetime
import time
import os

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

sw_url = 'https://www.glassdoor.com/Job/chicago-il-us-software-developer-jobs-SRCH_IL.0,13_IC1128808_KO14,32.htm'
da_url = 'https://www.glassdoor.com/Job/chicago-il-data-analyst-jobs-SRCH_IL.0,10_IC1128808_KO11,23.htm'
ds_url = 'https://www.glassdoor.com/Job/chicago-il-data-scientist-jobs-SRCH_IL.0,10_IC1128808_KO11,25.htm'
dteng_url = 'https://www.glassdoor.com/Job/chicago-il-data-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,24.htm'
cloud_url = 'https://www.glassdoor.com/Job/chicago-il-cloud-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,25.htm'
dvop_url = 'https://www.glassdoor.com/Job/chicago-il-dev-ops-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,27.htm'
mleng_url = 'https://www.glassdoor.com/Job/chicago-il-machine-learning-engineer-jobs-SRCH_IL.0,10_IC1128808_KO11,36.htm'
web_url = 'https://www.glassdoor.com/Job/chicago-il-web-developer-jobs-SRCH_IL.0,10_IC1128808_KO11,24.htm'

url_list = [sw_url, ds_url, da_url, dvop_url, mleng_url, cloud_url, web_url, dteng_url]

def save_progress(data_dict, filename):
    """Save current scraping progress to a CSV file."""
    df = pd.DataFrame(data_dict)
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)
        print(f"[Saved] Created {filename}")
    else:
        df.to_csv(filename, mode='a', header=False, index=False)
        print(f"[Saved] Appended to {filename}")


def scrape_page(driver,dic):

    job_column = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul[aria-label="Jobs List"]')))
    jobs = WebDriverWait(job_column, 3).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'li')))
    print(f'found {len(jobs)} job cards')

    added = 0

    for j in jobs:
        #print(j.text)
        id = j.id
        if id not in dic['ID']:
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
                dic["Title"].append(title)
                dic["Location"].append(location)
                dic["Salary"].append(salary)
                dic["Description"].append(description)
                dic["ID"].append(id)
                added += 1
    
    print(f'{added} jobs appended out of {len(jobs)} found')
    return added

def main():
    dics = {"Title": [], "Location": [], "Salary": [], "Description": [], "ID": []}
    fileNm = Path(f'GlassdoorPull-{datetime.date.today()}.csv')

    if fileNm.exists():
        write = input(f'{fileNm} already exists. Overwrite? (Y/N): ')
    else:
        write = 'y'

    print(f'Launching Chrome browser... write?: {write}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(1)

    try:
        for url in url_list:
            driver.get(url)
            jobListing = scrape_page(driver, dics)
            save_progress(dics, fileNm)  # Save after initial page

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
                jobListing = scrape_page(driver, dics)
                save_progress(dics, fileNm)  # Save after every scrape

    except Exception as e:
        print(f"[CRASH] Something went wrong: {e}")
        print("Saving progress before exiting...")
        save_progress(dics, fileNm)

    finally:
        driver.quit()
        print("Driver closed.")



if __name__ == "__main__":
    main()