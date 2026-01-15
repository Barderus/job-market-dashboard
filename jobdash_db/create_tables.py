from jobdash_db.db_connection import get_connection

create_tables = [
    """
    CREATE TABLE IF NOT EXISTS job_market (
        job_company VARCHAR(255),
        job_description LONGTEXT,
        job_type VARCHAR(64),
        job_location VARCHAR(255),
        job_salary VARCHAR(255),
        job_title VARCHAR(255),
        job_source VARCHAR(64),
        min_salary DOUBLE NULL,
        max_salary DOUBLE NULL,
        avg_salary DOUBLE NULL,
        city VARCHAR(255),
        state VARCHAR(64),
        country VARCHAR(64),
        job_skills LONGTEXT
        );
    """,

    """
    CREATE TABLE IF NOT EXISTS data_jobs (
        job_via VARCHAR(255),
        job_title_short VARCHAR(255),
        job_title VARCHAR(255),
        job_company VARCHAR(255),
        job_schedule_type VARCHAR(255),
        job_location VARCHAR(255),
        job_country VARCHAR(255),
        job_posted_date TEXT,
        job_work_from_home TEXT,
        salary_rate VARCHAR(32),
        salary_year_avg DOUBLE NULL,
        salary_hour_avg DOUBLE NULL,
        job_skills LONGTEXT
        );""",
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
