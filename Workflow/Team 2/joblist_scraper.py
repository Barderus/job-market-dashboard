from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Workflow.scraper_utils import append_rows, build_stealth_driver, make_job_row, make_output_file


output_file = make_output_file("joblist_output")

def scrape_page(driver, search_term, search_location, source_url):
    page_rows = []
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

                page_rows.append(
                    make_job_row(
                        source="joblist",
                        search_term=search_term,
                        search_location=search_location,
                        source_url=source_url,
                        title=title,
                        company_name=company,
                        job_location=location,
                    )
                )

            except NoSuchElementException:
                print("No such element while parsing a job card.")
            except Exception as e:
                print(f"[Job Error] {e}")

    except Exception as e:
        print(f"[Page Error] {e}")

    return page_rows


def next_page(driver):
    try:
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "css-1vk6oae"))
        )
        next_page_button.click()
        return True
    except NoSuchElementException:
        print("No more pages available")
        return False
    except Exception as e:
        print(f"[Next Page Error] {e}")
        return False


def main():
    driver = build_stealth_driver(detach=True)

    url_list = [
        ("software developer", "Chicago, IL", "https://www.joblist.com/search?l=Chicago%2C+IL&q=software+developer&lr=WITHIN_25_MILES"),
        ("software engineer", "Chicago, IL", "https://www.joblist.com/search?l=Chicago%2C+IL&q=software+engineer&lr=WITHIN_25_MILES&pid=internal"),
        ("data scientist", "Chicago, IL", "https://www.joblist.com/search?l=Chicago%2C+IL&q=data+scientist&lr=WITHIN_25_MILES&pid=internal"),
        ("machine learning engineer", "Chicago, IL", "https://www.joblist.com/search?l=Chicago%2C+IL&q=Machine+learning+engineer&lr=WITHIN_25_MILES&pid=internal"),
    ]

    try:
        for search_term, search_location, url in url_list:
            print(f"[Info] Visiting: {url}")
            driver.get(url)

            while True:
                page_rows = scrape_page(driver, search_term, search_location, url)
                append_rows(page_rows, output_file)

                if not next_page(driver):
                    break

    except Exception as e:
        print(f"[CRASH] Unexpected error: {e}")
        print("[Info] Saving progress before exiting...")

    finally:
        driver.quit()
        print("[Info] Chrome driver closed.")
