import random
import os
import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

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
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"
]


def save_progress(data_dict, filename='job_scrape_output.csv'):
    df = pd.DataFrame(data_dict)
    if not df.empty:
        if not os.path.exists(filename):
            df.to_csv(filename, index=False)
            print(f"[Saved] Created new file: {filename}")
        else:
            df.to_csv(filename, mode='a', header=False, index=False)
            print(f"[Saved] Appended to file: {filename}")
    else:
        print("[Warning] No data to save.")


def scrape_page(driver, job_dict):
    try:
        job_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-item.ov.css-15ystdb"))
        )

        for job in job_cards:
            try:
                title = WebDriverWait(job, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".itemHeaderUi.css-10w5g4p"))
                ).text.strip()

                company = job.find_element(By.CSS_SELECTOR, ".itemMetaUi.css-11t701e").text.strip()
                location = job.find_element(By.CSS_SELECTOR, ".itemMetaUi.css-gbogy6").text.strip()

                job_dict["title"].append(title)
                job_dict["company_name"].append(company)
                job_dict["job_location"].append(location)

            except NoSuchElementException:
                print("No such element while parsing a job card.")
            except Exception as e:
                print(f"[Job Error] {e}")

    except Exception as e:
        print(f"[Page Error] {e}")


def main():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-popup-blocking')
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
            fix_hairline=True)

    job_dict = {
        "title": [],
        "job_location": [],
        "company_name": []
    }

    url_list = [
        "https://www.monster.com/jobs/search?q=Software+developer&where=&page=1&so=m.h.lh",
        "https://www.joblist.com/search?l=Chicago%2C+IL&q=software+engineer&lr=WITHIN_25_MILES&pid=internal",
        "https://www.joblist.com/search?l=Chicago%2C+IL&q=data+scientist&lr=WITHIN_25_MILES&pid=internal",
        "https://www.joblist.com/search?l=Chicago%2C+IL&q=Machine+learning+engineer&lr=WITHIN_25_MILES&pid=internal"
    ]

    try:
        for url in url_list:
            print(f"[Info] Visiting: {url}")
            driver.get(url)
            scrape_page(driver, job_dict)
            save_progress(job_dict)

    except Exception as e:
        print(f"[CRASH] Unexpected error: {e}")
        print("[Info] Saving progress before exiting...")
        save_progress(job_dict)

    finally:
        driver.quit()
        print("[Info] Chrome driver closed.")
