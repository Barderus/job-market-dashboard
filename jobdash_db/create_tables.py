from jobdash_db.db_connection import get_connection

create_tables = [
    """
    CREATE TABLE IF NOT EXISTS job_market (
        job_title   VARCHAR(255),
        job_location    VARCHAR(255),
        job_company VARCHAR(255),
        job_schedule_type   VARCHAR(255),
        salary_rate     VARCHAR(255),
        min_salary      DOUBLE NULL,
        max_salary      DOUBLE NULL,
        salary_year_avg     DOUBLE NULL,
        job_country     VARCHAR(64),
        skills      LONGTEXT,
        job_skills  LONGTEXT,
        job_type_skills     LONGTEXT,
        salary_year     VARCHAR(255),
        salary_hourly   VARCHAR(255),
        salary_hour_avg     DOUBLE NULL,
        data_source     VARCHAR(255)
        );
    """,
    """
    CREATE TABLE IF NOT EXISTS data_jobs (
        job_title_short     VARCHAR(255),
        job_title       VARCHAR(255),
        job_location    VARCHAR(255),
        job_via     VARCHAR(255),
        job_schedule_type   VARCHAR(255),
        job_work_from_home  TINYINT(1),
        search_location     VARCHAR(255),
        job_country     VARCHAR(255),
        salary_rate     VARCHAR(255),
        salary_year_avg     DOUBLE NULL,
        salary_hour_avg     DOUBLE NULL,
        company_name        VARCHAR(255),
        job_skills      LONGTEXT,
        job_type_skills     LONGTEXT,
        data_source     VARCHAR(255)
        );
    """,
]


def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for statement in create_tables:
            cursor.execute(statement)
        print("Table created successfully")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(tables)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
