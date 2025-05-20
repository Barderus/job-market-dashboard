import os
import random
import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver

from datetime import datetime

# Generate a unique filename for this run
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = f"simplyhired_output_{timestamp}.csv"


# Exceptions to ignore when waiting for
# element searching to return a value
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

# Assuming there are 260 working days in a year...
YEARLY_WORK_DAYS = 260

# Assuming that x hours a day are worked on average...
DAILY_WORK_HOURS = 8

# List of user agent strings
user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
               "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
               "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"]

# Handy Stack Overflow page to help with
# handling elements that haven't loaded yet:
# https://stackoverflow.com/questions/27003423/staleelementreferenceexception-on-python-selenium

# WebDriverWait and expected_conditions are implemented
# below in accordance with the source above.

# Source to clarify proper use of implicit
# vs explicit waiting with Selenium:
# https://www.selenium.dev/documentation/webdriver/waits/

# This program only uses explicit waits
# via WebDriverWait, paired with
# time.sleep() as needed for operations
# where action needs to be halted even
# when current page elements are loaded.

# This answer was great for explaining when
# to use certain explicit wait functions:
# https://stackoverflow.com/questions/52603847/how-to-sleep-selenium-webdriver-in-python-for-milliseconds

# Wait to receive some existing WebElement
def wait_for_present_element(driver, by, search_term, timeout=9999, poll_frequency=0.15, ignored_exceptions=ignored_exceptions):
    return WebDriverWait(driver=driver,
                         timeout=timeout,
                         ignored_exceptions=ignored_exceptions).until(
                         EC.presence_of_element_located((by, search_term)))

# Wait to find some list of existing WebElements
def wait_for_present_elements(driver, by, search_term, timeout=9999, poll_frequency=0.15, ignored_exceptions=ignored_exceptions):
    return WebDriverWait(driver=driver,
                         timeout=timeout,
                         ignored_exceptions=ignored_exceptions).until(
                         EC.presence_of_all_elements_located((by, search_term)))

# Wait to receive some existing and visible WebElement
def wait_for_visible_element(driver, by, search_term, timeout=9999, poll_frequency=0.15, ignored_exceptions=ignored_exceptions):
    return WebDriverWait(driver=driver,
                         timeout=timeout,
                         ignored_exceptions=ignored_exceptions).until(
                         EC.visibility_of_element_located((by, search_term)))

# Wait to find some list of existing and visible WebElements
def wait_for_visible_elements(driver, by, search_term, timeout=9999, poll_frequency=0.15, ignored_exceptions=ignored_exceptions):
    return WebDriverWait(driver=driver,
                         timeout=timeout,
                         ignored_exceptions=ignored_exceptions).until(
                         EC.visibility_of_all_elements_located((by, search_term)))

# Wait until an WebElement is clickable using the WebElement
def wait_to_click(driver, timeout=9999, poll_frequency=0.15, ignored_exceptions=ignored_exceptions):
    return WebDriverWait(driver=driver,
                         timeout=timeout,
                         ignored_exceptions=ignored_exceptions).until(
                         EC.element_to_be_clickable(driver))

# Wait until an WebElement is clickable using By and a search term
def wait_to_click_by(driver, by, search_term, timeout=9999, poll_frequency=0.15, ignored_exceptions=ignored_exceptions):
    return WebDriverWait(driver=driver,
                         timeout=timeout,
                         ignored_exceptions=ignored_exceptions).until(
                         EC.element_to_be_clickable((by, search_term)))

# Clicks on the element specified so that
# a box containing its enlarged information
# appears on the right
def get_enlarged_info(driver: ChromeDriver, element: WebElement, old_box):
    try:
        clickable = wait_to_click_by(element, By.XPATH, ".//div")
        clickable.click()

        info_box = wait_for_visible_element(driver, By.CLASS_NAME, "flex-container")

        while (old_box is not None) and (old_box == info_box):
            try:
                info_box = wait_for_visible_element(driver, By.CLASS_NAME, "flex-container", 0.7, 0.2)

            except TimeoutException:
                print("MomentaryTimeout")
                continue

            except NoSuchElementException:
                print("LoopElementException")
                continue

            except StaleElementReferenceException:
                print("LoopStaleException")
                continue
        
        return info_box

    except NoSuchElementException:
        print("Whoops! Clickable object or resulting container not found!")

    except StaleElementReferenceException:
        print("Element no longer detected: info enlargement operation")

# Handy Selenium documentation
# providing help with locators:
# https://www.selenium.dev/documentation/test_practices/encouraged/locators/

# List of ways to wait for a page:
# https://www.browserstack.com/guide/selenium-wait-for-page-to-load

# Where the action is at B)
def scrape_page(driver: ChromeDriver, job_dict):
    try:
        # Gets the unordered list with list elements
        # containing job info that's on each page.
        job_entries = wait_for_visible_element(driver, By.ID, "job-list")

        # Gets each individual list element inside
        # job_entries.
        elements = wait_for_visible_elements(job_entries, By.TAG_NAME, "li")

        info_box = None
    
        for element in elements:
            try:
                # Stores the expanded info for the current job listing :D
                info_box = get_enlarged_info(driver, element, info_box)

                # Scrapes info from the current enlarged info box
                # and stores it in our dictionary of job info :D

                # New methods for searching
                # field info, courtesty of Mike
                #job_dict["Unique Title"].append("SoftDev")
                job_dict["Title"].append(wait_for_visible_element(element, By.TAG_NAME, "a").text.strip())
                job_dict["Job Location"].append(wait_for_visible_element(element, By.CLASS_NAME, "css-1t92pv").text.strip())
                job_dict["Company Name"].append(wait_for_visible_element(element, By.CSS_SELECTOR, 'span[data-testid="companyName"]').text.strip())
                
                try:
                    job_dict["Job Type"].append(wait_for_visible_element(info_box, By.CSS_SELECTOR, 'span[data-testid="viewJobBodyJobDetailsJobType"]', 0.065, 0.01).text.strip())

                except TimeoutException:
                    print("Job Type Unknown")
                    job_dict["Job Type"].append("unknown")

                try:
                    job_dict["Salary"].append(wait_for_visible_element(info_box, By.CSS_SELECTOR, 'span[data-testid="viewJobBodyJobCompensation"]', 0.065, 0.01).text.strip())

                except TimeoutException:
                    print("Salary Unknown")
                    job_dict["Salary"].append("unknown")

                # Copy-paste for getting data for new field:
                # job_dict["FIELD"].append(wait_for_visible_element(info_box, By.SOMETHING, "SEARCH_TERM").text.strip())
                
            except NoSuchElementException:
                print("Whoops! Job element not found!")

            except StaleElementReferenceException:
                print("Element no longer detected: scrape inner operations")
        
    except NoSuchElementException:
        print("Page structure misalignment!")
    
    except StaleElementReferenceException:
        print("Element no longer detected: scrape outer operations")

# Navigates to the next page.
# Simple enough, right? Heh...
def next_page(driver: ChromeDriver):
    try:
        clickable = wait_to_click_by(driver, By.CLASS_NAME, "css-1puj5o8")
        clickable.click()

    except NoSuchElementException:
        print("Next Page structure misalignment!")

    except StaleElementReferenceException:
        print("Element no longer detected: next page operations")

# Waits for the next page to load,
# then returns the new page number
def wait_for_next_page(driver: ChromeDriver, current_page: int) -> int:
    page_number: int = 0
    try:
        while page_number <= current_page:
            try:
                page_navigation = wait_for_visible_element(driver, By.CLASS_NAME, "css-1hog1e3", 0.7, 0.5)
                current_page_element = wait_for_visible_element(page_navigation, By.TAG_NAME, "span", 0.7, 0.5)

                page_number = int(current_page_element.text.strip())
                print(f'Page number: {page_number}')
            
            except (TimeoutException):
                print("Ticking...")
                continue
            
            except (NoSuchElementException, StaleElementReferenceException):
                print("Skipping...")
                continue
        
    except NoSuchElementException:
        print("Page Navigation structure misalignment!")

    except StaleElementReferenceException:
        print("Element no longer detected: page wait operations")
    
    return page_number

# Getting a dictionary of float values
# representing the maximum and minimum
# salary for each position. Positions
# without pay listed default to $0.

# It is assumed that any salary which
# includes both a 'K' and a '.' only
# goes one decimal place to the right.

# Removed parse_salary_info since there is no need for this calculation. It might lead to false salaries.
"""
def parse_salary_info(listings: list):
    salary_min_max = {
        "Salary Minimum": [],
        "Salary Maximum": []
    }

    for listing in listings:
        if "unknown" not in listing:
            if listing.find('-') >= 0:
                salary_min, salary_max = listing.split('-')
                if ('K' in salary_min) and ('.' in salary_min):
                    salary_min = float("".join(filter(lambda x: x in '0123456789', salary_min.replace('K', "00"))))
                elif 'K' in salary_min:
                    salary_min = float("".join(filter(lambda x: x in '0123456789', salary_min.replace('K', "000"))))
                else:
                    salary_min = float("".join(filter(lambda x: x in '.0123456789', salary_min)))
                
                if ('K' in salary_max) and ('.' in salary_max):
                    salary_max = float("".join(filter(lambda x: x in '0123456789', salary_max.replace('K', "00"))))
                elif 'K' in salary_max:
                    salary_max = float("".join(filter(lambda x: x in '0123456789', salary_max.replace('K', "000"))))
                else:
                    salary_max = float("".join(filter(lambda x: x in '.0123456789', salary_max)))

                if "an hour" in listing:
                    salary_min_max["Salary Minimum"].append(salary_min * YEARLY_WORK_DAYS * DAILY_WORK_HOURS)
                    salary_min_max["Salary Maximum"].append(salary_max * YEARLY_WORK_DAYS * DAILY_WORK_HOURS)

                elif "a day" in listing:
                    salary_min_max["Salary Minimum"].append(salary_min * YEARLY_WORK_DAYS)
                    salary_min_max["Salary Maximum"].append(salary_max * YEARLY_WORK_DAYS)
                
                else:
                    salary_min_max["Salary Minimum"].append(salary_min)
                    salary_min_max["Salary Maximum"].append(salary_max)

            else:
                if ('K' in listing) and ('.' in listing):
                    salary = float("".join(filter(lambda x: x in '0123456789', listing.replace('K', "00"))))
                elif 'K' in listing:
                    salary = float("".join(filter(lambda x: x in '0123456789', listing.replace('K', "000"))))
                else:
                    salary = float("".join(filter(lambda x: x in '.0123456789', listing)))

                if "an hour" in listing:
                    salary_min_max["Salary Minimum"].append(salary * YEARLY_WORK_DAYS * DAILY_WORK_HOURS)
                    salary_min_max["Salary Maximum"].append(salary * YEARLY_WORK_DAYS * DAILY_WORK_HOURS)

                elif "a day" in listing:
                    salary_min_max["Salary Minimum"].append(salary * YEARLY_WORK_DAYS)
                    salary_min_max["Salary Maximum"].append(salary * YEARLY_WORK_DAYS)

                else:
                    salary_min_max["Salary Minimum"].append(salary)
                    salary_min_max["Salary Maximum"].append(salary)

        else:
            salary_min_max["Salary Minimum"].append(0.0)
            salary_min_max["Salary Maximum"].append(0.0)
    
    return pd.DataFrame(salary_min_max)
"""

def main():
    # How many pages to search
    pages_to_search = 2

    # Establishing our dictionary of job listing data
    job_dict = {
        #"Unique Title": [],         # Unique job title
        "Title": [],                # Title of the job
        "Job Location": [],         # Location ( State )
        "Company Name": [],         # Company name
        "Job Type": [],             # Whether full-time, part-time, intern
        #"Remote": [],               # Remote, in-person, hybrid
        #"Wage": [],                 # $ per hour
        "Salary": [],               # $ per year
        #"Education": [],            # Undergrad, master, phd
        #"Languages": [],            # Programming languages
        #"Frameworks": [],           # React, Angular, Django, Flask, etc
        #"Other": []                 # Database, Cloud technologies, etc
    }
    
    # Setting up Chrome Options
    chrome_options = Options()

    # Start the window to open maximized
    chrome_options.add_argument("start-maximized")

    # These options are critical in avoiding
    # detection. They make it seem like we are
    # not automating a page and help us appear
    # to share much more likeness to a normal
    # user as we scrape.
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

    # The "--headless" argument means that the
    # scraping will occur without showing the
    # window of the browser while it happens.
    # Chrome has an old and new version of
    # headless operation. The argument
    # "--headless=new" uses the newer version.

    # Uncomment the below line to run the
    # scraping with headless navigation.
    # chrome_options.add_argument("--headless=new")

    # Choose a random User-Agent from the list
    # and add it to our options
    random_user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"--user-agent={random_user_agent}")

    # Initializing our webdriver :D
    driver = webdriver.Chrome(options=chrome_options)

    # Use of selenium-stealth to aid
    # in our avoidance of detection
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # The URL to visit
    sw_url = "https://www.simplyhired.com/search?q=software+developer&l=Chicago%2C+IL"
    da_url = "https://www.simplyhired.com/search?q=data+analyst&l=Chicago%2C+IL"
    ds_url = "https://www.simplyhired.com/search?q=data+science&l=Chicago%2C+IL"
    dteng_url = "https://www.simplyhired.com/search?q=data+engineer&l=Chicago%2C+IL"
    cloud_url = "https://www.simplyhired.com/search?q=cloud+computing&l=Chicago%2C+IL"
    dvop_url = "https://www.simplyhired.com/search?q=devops&l=Chicago%2C+IL"
    mleng_url = "https://www.simplyhired.com/search?q=machine+learning+engineer&l=Chicago%2C+IL"
    web_url = "https://www.simplyhired.com/search?q=web+developer&l=Chicago%2C+IL"

    url_list = [sw_url, ds_url, da_url, dvop_url, mleng_url, cloud_url, web_url, dteng_url]

    # Visiting target website
    for url in url_list:
        driver.get(url)

        # Our action loop!
        # Runs the functions defined
        # throughout this document
        # to scrape the specified
        # website (SimplyHired).
        current_page = 1
        while current_page <= pages_to_search:
            # Scrape data from the current page
            scrape_page(driver, job_dict)

            # Create a DataFrame for the current page's data
            listings_frame = pd.DataFrame(job_dict)

            if not os.path.isfile(output_file):
                listings_frame.to_csv(output_file, index=False)
                print(f"[Saved] Created new file: {output_file}")
            else:
                listings_frame.to_csv(output_file, mode='a', header=False, index=False)
                print(f"[Saved] Appended to file: {output_file}")

            # Go to the next page
            next_page(driver)

            # Update the current page
            current_page = wait_for_next_page(driver, current_page)

    #salary_frame = parse_salary_info(job_dict["Salary"])
    #salary_frame["Salary Minimum"] = pd.to_numeric(salary_frame["Salary Minimum"], downcast="float", errors="coerce")
    #salary_frame["Salary Maximum"] = pd.to_numeric(salary_frame["Salary Maximum"], downcast="float", errors="coerce")

    #listings_sortable_frame = pd.concat([listings_frame, salary_frame], axis=1)
    #print(listings_sortable_frame.sort_values(by=["Salary Minimum"], ascending=False))


if __name__ == '__main__':
    main()