import random

import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Generate a unique filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = f"zip-recruiter-pull-{timestamp}.csv"


# List of user agents string
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"]

base_url = "https://www.ziprecruiter.com/jobs-search?search="

def save_progress(data_dict, filename):
    df = pd.DataFrame(data_dict)
    if not df.empty:
        if not os.path.exists(filename):
            df.to_csv(filename, index=False)
            print(f"[Saved] Created new file {filename}")
        else:
            df.to_csv(filename, mode='a', header=False, index=False)
            print(f"[Saved] Appended data to {filename}")
    else:
        print("[Warning] No data to save.")



def scrape_page(driver, job_dict, url):
    # Get the current window handle before any click
    main_window_handle = driver.current_window_handle

    job_cards_selector = '*[class*="job_result_two_pane"]'
    try:
        # Locate job cards initially
        job_cards = driver.find_elements(By.CSS_SELECTOR, job_cards_selector)
    except Exception as e:
        print(f"Error locating job cards: {e}")
        return

    i = 0
    while i < len(job_cards):
        try:
            # Re-fetch job cards to ensure fresh references
            job_cards = driver.find_elements(By.CSS_SELECTOR, job_cards_selector)

            if i >= len(job_cards):
                print(f"Job card index {i} is out of range. Skipping.")
                break

            job = job_cards[i]

            # Scroll into view and click the job card
            driver.execute_script("arguments[0].scrollIntoView(true);", job)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, job_cards_selector)))
            job.click()

            # Wait until the URL changes
            WebDriverWait(driver, 10).until(EC.url_changes(url))

            # Navigate back to the original page if it is redirected somewhere else
            new_url = driver.current_url
            if base_url not in new_url:
                print(f"Page has redirected to: {new_url}")

                driver.get(url)

            # Extract job details
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='right-pane']")))
            job_title = driver.find_element(By.CSS_SELECTOR,
                                            "h1.font-bold.text-primary.text-header-md.md\:text-header-md-tablet").text
            job_location = driver.find_element(By.CSS_SELECTOR,
                                               "div.mb-24 p.text-primary.normal-case.text-body-md").text
            company_name = driver.find_element(By.CSS_SELECTOR,
                                               "div.flex.justify-between.items-start a.text-primary").text

            job_details = driver.find_element(By.CSS_SELECTOR,
                                              "div.text-primary.whitespace-pre-line.break-words").text
            #print(job_details)
            # Extract salary and job type
            job_salary = None
            job_type = None

            # Look for the salary range
            salary_elements = driver.find_elements(By.CSS_SELECTOR,
                                                   "div.flex.gap-x-12 p.text-primary.normal-case.text-body-md")
            for elem in salary_elements:
                text = elem.text.strip()
                if text.startswith('$'):
                    job_salary = text
                elif text.lower() in ["full-time", "part-time"]:
                    job_type = text

            # If both information exists, add them to the job_dict
            job_dict["title"].append(job_title)
            job_dict["company_name"].append(company_name)
            job_dict["job_location"].append(job_location)
            job_dict["job_salary"].append(job_salary)
            job_dict["job_type"].append(job_type)
            job_dict["job_description"].append(job_details)

            i += 1  # Increment the index only if the click and extraction were successful

        except StaleElementReferenceException:
            print(f"Stale reference encountered for job card {i + 1}. Retrying.")
        except Exception as e:
            print(f"An unexpected error occurred on job card {i + 1}: {e}")
            i += 1  # Skip to the next job card if an error occurs


def next_page(driver):
    try:
        # Wait for the "Next Page" button to become clickable
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Next Page']"))
        )
        next_page_button.click()
        return True
    except TimeoutException:
        print("No more pages available.")
        return False


def main():
    import os
    from pathlib import Path

    url_list = [
        "https://www.ziprecruiter.com/jobs-search?search=software+engineer&location=Chicago%2C+IL&lvk=JG_74EGAdtycohHKniD2eg.--NacsUqfMF",
        "https://www.ziprecruiter.com/jobs-search?search=data+scientist&location=Chicago%2C+IL&lvk=DBml3W3I7MdIbFS0oJWb1g.--Nfet94gmo",
        "https://www.ziprecruiter.com/jobs-search?search=data+analyst&location=Chicago%2C+IL&lvk=aJd0EasHdgwWMwd02uxqQw.--NfetAEI3k",
        "https://www.ziprecruiter.com/jobs-search?search=dev+ops&location=Chicago%2C+IL&lvk=8Fn5DTVbgDPdaWpheHFmCQ.--Nfe4Q0T8g",
        "https://www.ziprecruiter.com/jobs-search?search=machine+learning+engineer&location=Chicago%2C+IL&lvk=MOx4LHDzHjJ-JTykfwkowA.--NfetAqkTB",
        "https://www.ziprecruiter.com/jobs-search?search=cloud+engineer&location=Chicago%2C+IL&lvk=8Fn5DTVbgDPdaWpheHFmCQ.--Nfe4Q0T8g",
        "https://www.ziprecruiter.com/jobs-search?search=web+developer&location=Chicago%2C+IL&lvk=vGvBRpEKvrSltPTb5j8_iQ.--NffGxO2Yg",
        "https://www.ziprecruiter.com/jobs-search?search=data+engineer&location=Chicago%2C+IL&lvk=3kz6loGNfWcrdiKNC_NEBw.--Nfeszg53B"
    ]

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    job_dict = {
        "title": [],
        "job_location": [],
        "company_name": [],
        "job_type": [],
        "job_description": [],
        "job_salary": [],
    }

    try:
        for url in url_list:
            driver.get(url)
            element = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'content'))
            )
            ActionChains(driver).move_to_element(element).click().perform()

            page = 0
            while True:
                print(f"\n[Info] Scraping page {page + 1} from: {url}")
                scrape_page(driver, job_dict, url)
                save_progress(job_dict, output_file)

                if not next_page(driver):
                    print("No more pages to scrape for this job role.")
                    break

                url = driver.current_url
                page += 1

    except Exception as e:
        print(f"[CRASH] Error occurred: {e}")
        print("[Info] Saving progress before exiting...")
        save_progress(job_dict, output_file)

    finally:
        driver.quit()
        print("[Info] Driver closed.")


if __name__ == '__main__':
    main()
