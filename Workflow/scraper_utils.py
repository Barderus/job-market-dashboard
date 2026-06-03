import os
import random
from datetime import datetime
from typing import Mapping, Sequence

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0",
]

STANDARD_COLUMNS = [
    "source",
    "search_term",
    "search_location",
    "source_url",
    "scraped_at",
    "title",
    "company_name",
    "job_location",
    "job_type",
    "salary",
    "description",
]


def make_output_file(prefix: str, extension: str = "csv") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{timestamp}.{extension}"


def make_job_row(
    *,
    source: str,
    search_term: str,
    search_location: str,
    source_url: str,
    title: str | None = None,
    company_name: str | None = None,
    job_location: str | None = None,
    job_type: str | None = None,
    salary: str | None = None,
    description: str | None = None,
) -> dict[str, object]:
    return {
        "source": source,
        "search_term": search_term,
        "search_location": search_location,
        "source_url": source_url,
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
        "title": title,
        "company_name": company_name,
        "job_location": job_location,
        "job_type": job_type,
        "salary": salary,
        "description": description,
    }


def append_rows(rows: Sequence[Mapping[str, object]], filename: str) -> None:
    if not rows:
        print("[Warning] No data to save.")
        return

    output_path = filename
    is_new_file = not os.path.exists(output_path)
    df = pd.DataFrame(rows).reindex(columns=STANDARD_COLUMNS)
    df.to_csv(output_path, mode="a", header=is_new_file, index=False)
    action = "Created new file" if is_new_file else "Appended to file"
    print(f"[Saved] {action}: {output_path}")


def build_stealth_driver(detach: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if detach:
        chrome_options.add_experimental_option("detach", True)

    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options,
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver
