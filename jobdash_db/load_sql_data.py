import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.engine import URL
import traceback


load_dotenv()


def make_engine():
    user=os.getenv("MYSQL_USER")
    password=os.getenv("MYSQL_PASSWORD")
    host=os.getenv("MYSQL_HOST", "127.0.0.1")
    database=os.getenv("MYSQL_DB")

    url = URL.create(
        drivername="mysql+mysqlconnector",
        username=user,
        password=password,
        host=host,
        database=database,
    )
    return create_engine(url, pool_pre_ping=True)

def load_job_market_data(engine, df):
    df = df.reset_index(drop=True)
    print(df.columns.tolist())

    table_cols = [
        "job_company",
        "job_description",
        "job_type",
        "job_location",
        "job_salary",
        "job_title",
        "job_source",
        "min_salary",
        "max_salary",
        "avg_salary",
        "city",
        "state",
        "country",
        "job_skills",
    ]

    for c in table_cols:
        if c not in df.columns:
            df[c] = None

    df = df[table_cols].where(pd.notna(df), None)

    print(f"Uploading job_market: {len(df):,} rows")
    df.to_sql(
        "job_market",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )
    print("job_market upload complete.")

def load_data_jobs(engine, df):
    df = df.reset_index(drop=True)
    print(df.columns.tolist())

    required_cols = [
        "job_via",
        "job_title_short",
        "job_title",
        "job_company",
        "job_schedule_type",
        "job_location",
        "job_country",
        "job_posted_date",
        "job_work_from_home",
        "salary_rate",
        "salary_year_avg",
        "salary_hour_avg",
        "job_skills",
    ]
    for c in required_cols:
        if c not in df.columns:
            df[c] = None

    df = df[required_cols].where(pd.notna(df), None)

    df.to_sql(
        "data_jobs",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )
    print("data_jobs upload complete.")

def main():
    engine = make_engine()

    job_market_data = pd.read_csv("../Data/merger/job_market_processed_data.csv")
    data_jobs = pd.read_csv("../Data/merger/data_jobs.csv")

    try:
        load_data_jobs(engine, data_jobs)
    except Exception as e:
        print("ERROR TYPE:", type(e))
        print("ERROR:", e)
        traceback.print_exc(limit=5)

        #load_data_jobs(engine, data_jobs)

if __name__ == "__main__":
    main()