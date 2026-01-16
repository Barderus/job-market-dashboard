from jobdash_db.db_connection import get_connection

DDL_STATEMENT = """
    CREATE TABLE merged_jobs AS
    SELECT
        job_title_short,
        job_title,
        job_location,
        job_via,
        job_schedule_type,
        job_work_from_home,
        search_location,
        job_country,
        salary_rate,
        NULL AS salary_year,
        NULL AS salary_hourly,
        salary_year_avg,
        salary_hour_avg,
        NULL AS min_salary,
        NULL AS max_salary,
        company_name,
        job_skills,
        job_type_skills,
        data_source
    FROM data_jobs
    UNION ALL
    SELECT 
        NULL AS job_title_short,
        job_title,
        job_location,
        NULL AS job_via,
        job_schedule_type,
        NULL AS job_work_from_home,
        NULL AS search_location,
        job_country,
        salary_rate,
        salary_year,
        salary_hourly,
        salary_year_avg,
        salary_hour_avg,
        min_salary,
        max_salary,
        job_company, 
        job_skills,
        job_type_skills,
        data_source
    FROM job_market
    """

def main():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(DDL_STATEMENT)
    print("Merged tables successfully")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()

