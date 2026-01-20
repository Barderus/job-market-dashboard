top_US_roles = """
    SELECT *
    FROM v_top_paying_roles_by_country
    WHERE job_country = 'United States'
     AND salary_rank_in_country <= 10
    ORDER BY salary_rank_in_country; \
    """

top_companies = """
    SELECT *
    FROM v_top_companies_by_role
    WHERE job_title_short = 'Data Scientist'
     AND company_rank_in_role <= 10
    ORDER BY company_rank_in_role; \
    """

roles_demanded = """
    SELECT
      job_title_short,
      COUNT(*) AS postings,
      AVG(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS avg_salary_year
    FROM merged_jobs
    WHERE job_title_short IS NOT NULL
    GROUP BY job_title_short
    ORDER BY postings DESC
    LIMIT 20; \
    """

roles_per_pay = """
    SELECT
       job_title_short,
       COUNT(*) AS postings_with_salary,
       AVG(salary_year_norm) AS avg_salary_year
    FROM merged_jobs
    WHERE job_title_short IS NOT NULL
     AND salary_year_norm IS NOT NULL
     AND salary_is_outlier = 0
    GROUP BY job_title_short
    HAVING COUNT(*) >= 500
    ORDER BY avg_salary_year DESC
    LIMIT 20; \
    """

INSIGHTS_SQL = [
    ("top_US_roles", top_US_roles),
    ("top_companies", top_companies),
    ("roles_demanded", roles_demanded),
    ("roles_per_pay", roles_per_pay),
]
