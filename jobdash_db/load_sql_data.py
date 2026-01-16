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

def load_job_market_data(engine, df2):
    df2 = df2.reset_index(drop=True)
    print(df2.columns.tolist())

    table_cols = [
        "job_title",
        "job_location",
        "job_company",
        "job_schedule_type",
        "salary_rate",
        "min_salary",
        "max_salary",
        "salary_year_avg",
        "salary_hour_avg",
         "job_country",
        "job_skills",
        "job_type_skills",
        "salary_year",
        "salary_hourly",
        "data_source"
    ]

    # ensure all required columns exist
    for c in table_cols:
        if c not in df2.columns:
            df2[c] = None

    # convert NaN to None for SQL NULL
    out = df2[table_cols].where(pd.notna(df2[table_cols]), None)

    print(f"Uploading job_market: {len(out):,} rows")
    out.to_sql(
        "job_market",
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi",
    )
    print("job_market upload complete.")

def load_data_jobs(engine, df):
    df = df.reset_index(drop=True)
    print(df.columns.tolist())

    required_cols = [
        "job_title_short",
        "job_title",
        "job_location",
        "job_via",
        "job_schedule_type",
        "job_work_from_home",
        "search_location",
        "job_country",
        "salary_rate",
        "salary_year_avg",
        "salary_hour_avg",
        "company_name",
        "job_skills",
        "job_type_skills",
        "data_source",
    ]

    for c in required_cols:
        if c not in df.columns:
            df[c] = None

    out = df[required_cols].where(pd.notna(df[required_cols]), None)

    print(f"Uploading data_jobs: {len(out):,} rows")
    out.to_sql(
        "data_jobs",
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=500,
        method="multi",
    )
    print("data_jobs upload complete.")


def main():
    engine = make_engine()

    job_market_data = pd.read_csv("../Data/merger/job_market_processed_data.csv")
    job_market_data["data_source"] = "job_market" # To ensure we can track where the row came from

    data_jobs = pd.read_csv("../Data/merger/data_jobs.csv")
    data_jobs["data_source"] = "data_jobs"

    try:
        load_job_market_data(engine, job_market_data)
    except Exception as e:
        print("ERROR TYPE:", type(e))
        print("ERROR:", e)
        traceback.print_exc(limit=10)

    try:
        load_data_jobs(engine, data_jobs)
    except Exception as e:
        print("ERROR TYPE:", type(e))
        print("ERROR:", e)
        traceback.print_exc(limit=10)

if __name__ == "__main__":
    main()