import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def make_engine():
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    database=os.getenv("MYSQL_DB"),

    url = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
    return create_engine(url, pool_pre_ping=True)


def main():
    engine = make_engine()

    job_market_data = pd.read_csv("../Data/merger/job_market_processed_data.csv")
    data_jobs = pd.read_csv("../Data/merger/data_jobs.csv")

if __name__ == "__main__":
    main()