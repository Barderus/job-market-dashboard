from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from Workflow.scraper_utils import append_rows, build_stealth_driver, make_job_row, make_output_file


output_file = make_output_file("zip-recruiter-pull")

base_url = "https://www.ziprecruiter.com/jobs-search?search="

def scrape_page(driver, url, search_term, search_location):
    # Get the current window handle before any click
    main_window_handle = driver.current_window_handle

    job_cards_selector = '*[class*="job_result_two_pane"]'
    page_rows = []
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
                                            r"h1.font-bold.text-primary.text-header-md.md\:text-header-md-tablet").text
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
            page_rows.append(
                make_job_row(
                    source="ziprecruiter",
                    search_term=search_term,
                    search_location=search_location,
                    source_url=url,
                    title=job_title,
                    company_name=company_name,
                    job_location=job_location,
                    job_type=job_type,
                    salary=job_salary,
                    description=job_details,
                )
            )

            i += 1  # Increment the index only if the click and extraction were successful

        except StaleElementReferenceException:
            print(f"Stale reference encountered for job card {i + 1}. Retrying.")
        except Exception as e:
            print(f"An unexpected error occurred on job card {i + 1}: {e}")
            i += 1  # Skip to the next job card if an error occurs

    return page_rows


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
    url_list = [
        ("software engineer", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=software+engineer&location=Chicago%2C+IL&lvk=JG_74EGAdtycohHKniD2eg.--NacsUqfMF"),
        ("data scientist", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=data+scientist&location=Chicago%2C+IL&lvk=DBml3W3I7MdIbFS0oJWb1g.--Nfet94gmo"),
        ("data analyst", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=data+analyst&location=Chicago%2C+IL&lvk=aJd0EasHdgwWMwd02uxqQw.--NfetAEI3k"),
        ("dev ops", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=dev+ops&location=Chicago%2C+IL&lvk=8Fn5DTVbgDPdaWpheHFmCQ.--Nfe4Q0T8g"),
        ("machine learning engineer", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=machine+learning+engineer&location=Chicago%2C+IL&lvk=MOx4LHDzHjJ-JTykfwkowA.--NfetAqkTB"),
        ("cloud engineer", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=cloud+engineer&location=Chicago%2C+IL&lvk=8Fn5DTVbgDPdaWpheHFmCQ.--Nfe4Q0T8g"),
        ("web developer", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=web+developer&location=Chicago%2C+IL&lvk=vGvBRpEKvrSltPTb5j8_iQ.--NffGxO2Yg"),
        ("data engineer", "Chicago, IL", "https://www.ziprecruiter.com/jobs-search?search=data+engineer&location=Chicago%2C+IL&lvk=3kz6loGNfWcrdiKNC_NEBw.--Nfeszg53B"),
    ]

    driver = build_stealth_driver(detach=True)

    try:
        for search_term, search_location, url in url_list:
            driver.get(url)
            element = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'content'))
            )
            ActionChains(driver).move_to_element(element).click().perform()

            page = 0
            while True:
                print(f"\n[Info] Scraping page {page + 1} from: {url}")
                page_rows = scrape_page(driver, url, search_term, search_location)
                append_rows(page_rows, output_file)

                if not next_page(driver):
                    print("No more pages to scrape for this job role.")
                    break

                url = driver.current_url
                page += 1

    except Exception as e:
        print(f"[CRASH] Error occurred: {e}")
        print("[Info] Saving progress before exiting...")

    finally:
        driver.quit()
        print("[Info] Driver closed.")


if __name__ == '__main__':
    main()
