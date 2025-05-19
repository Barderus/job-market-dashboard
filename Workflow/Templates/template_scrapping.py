"""
    This template file contains a few functions to help with web scraping
        * scrape_page()
            This function's purpose is to scrape a webpage as the name suggests
        * next_page()
            This function's purpose is to click on an element to move to the next page
        * scroll_down()
            This function handle webpages that needs to scroll down to load new content
        * main()
            You can find here the main the dataframe we are using for this project
"""

import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# List of user agents string
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

def scrape_page():
    pass

def next_page(driver):
    try:
        next_page_button = driver.find_element("Enter the tag here")
        next_page_button.click()
        return True
    except NoSuchElementException:
        return False

def scroll_down(driver):
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        driver.implicitly_wait(5)  # Wait 5 seconds

        # Get the new height and compare with last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scrape_page()
            break
        last_height = new_height


def main():
    # Set up Chrome options
    chrome_options = Options()
    # Choose a random User-Agent from the list
    random_user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"--user-agent={random_user_agent}")

    #driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)

    job_dict = {"unique_title":[],          # Unique job title
                "title": [],                # Title of the job
                "job_location": [],         # Location ( State )
                "company_name": [],         # Company name
                "job_type": [],             # Whether full-time, part-time, intern
                "remote": [],               # Remote, in-person, hybrid
                "wage": [],                 # $ per hour
                "salary": [],               # $ per year
                "education": [],            # Undergrad, master, phd
                "prog_language": [],        # Programming languages
                "framework": [],            # React, Angular, Django, Flask, etc
                "others":[]                 # Database, Cloud technologies, etc
                }

    url = "Enter the URL here"
    # Visit target website
    driver.get(url)

    df = pd.DataFrame(job_dict)


if __name__ == '__main__':
    main()