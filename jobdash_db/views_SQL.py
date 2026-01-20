role_kpi = """
   CREATE OR REPLACE VIEW v_role_kpis AS
   SELECT
       job_title_short,
       COUNT(*) AS postings,
       SUM(COALESCE(job_work_from_home, 0) = 1) AS remote_postings,
       ROUND(100 * AVG(COALESCE(job_work_from_home, 0)), 2) AS pct_remote,
       AVG(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS avg_salary_year,
       AVG(CASE WHEN salary_is_outlier = 0 THEN salary_hour_norm END) AS avg_salary_hour
   FROM merged_jobs
   WHERE job_title_short IS NOT NULL
   GROUP BY job_title_short; \
   """


role_per_country = """
   CREATE OR REPLACE VIEW v_country_role AS
   SELECT
       job_country,
       job_title_short,
       COUNT(*) AS postings,
       ROUND(100 * AVG(COALESCE(job_work_from_home, 0)), 2) AS pct_remote,
       AVG(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS avg_salary_year
   FROM merged_jobs
   WHERE job_country IS NOT NULL
     AND job_title_short IS NOT NULL
   GROUP BY job_country, job_title_short; \
   """


company_summary = """
  CREATE OR REPLACE VIEW v_company_summary AS
  SELECT
      company_name,
      COUNT(*) AS postings,
      COUNT(DISTINCT job_title_short) AS distinct_roles,
      COUNT(DISTINCT job_country) AS distinct_countries,
      ROUND(100 * AVG(COALESCE(job_work_from_home, 0)), 2) AS pct_remote,
      AVG(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS avg_salary_year
  FROM merged_jobs
  WHERE company_name IS NOT NULL
  GROUP BY company_name; \
  """


role_salary = """
  CREATE OR REPLACE VIEW v_role_salary_summary AS
  SELECT
      job_title_short,
      COUNT(*) AS postings,
      SUM(salary_year_norm IS NOT NULL) AS postings_with_salary,
      ROUND(100 * SUM(salary_year_norm IS NOT NULL) / COUNT(*), 2) AS pct_with_salary,
      AVG(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS avg_salary_year,
      MIN(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS min_salary_year,
      MAX(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS max_salary_year
  FROM merged_jobs
  WHERE job_title_short IS NOT NULL
  GROUP BY job_title_short; \
  """


company_hiring_power = """
   CREATE OR REPLACE VIEW v_company_hiring_power AS
   SELECT
       company_name,
       COUNT(*) AS postings,
       COUNT(DISTINCT job_title_short) AS distinct_roles,
       COUNT(DISTINCT job_country) AS countries,
       ROUND(100 * AVG(COALESCE(job_work_from_home, 0)), 2) AS pct_remote,
       AVG(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS avg_salary_year
   FROM merged_jobs
   WHERE company_name IS NOT NULL
   GROUP BY company_name; \
   """

top_roles = """
    CREATE OR REPLACE VIEW v_top_paying_roles_by_country AS
    WITH role_country AS (
        SELECT
            job_country,
            job_title_short,
            COUNT(*) AS postings,
            AVG(CASE WHEN salary_is_outlier = 0 THEN salary_year_norm END) AS avg_salary_year
        FROM merged_jobs
        WHERE job_country IS NOT NULL
          AND job_title_short IS NOT NULL
          AND salary_year_norm IS NOT NULL
        GROUP BY job_country, job_title_short
    )
    SELECT
        job_country,
        job_title_short,
        postings,
        avg_salary_year,
        DENSE_RANK() OVER (
            PARTITION BY job_country
            ORDER BY avg_salary_year DESC
            ) AS salary_rank_in_country
    FROM role_country; \
    """

top_companies = """
    CREATE OR REPLACE VIEW v_top_companies_by_role AS
    WITH company_role AS (
        SELECT
            job_title_short,
            company_name,
            COUNT(*) AS postings
        FROM merged_jobs
        WHERE job_title_short IS NOT NULL
          AND company_name IS NOT NULL
        GROUP BY job_title_short, company_name
    )
    SELECT
        job_title_short,
        company_name,
        postings,
        DENSE_RANK() OVER (
            PARTITION BY job_title_short
            ORDER BY postings DESC
            ) AS company_rank_in_role
    FROM company_role; \
    """



VIEWS_SQL = [
    ("role_kpi", role_kpi),
    ("role_per_country", role_per_country),
    ("company_summary", company_summary),
    ("role_salary", role_salary),
    ("company_hiring_power", company_hiring_power),
    ("top_roles", top_roles),
    ("top_companies", top_companies),
]
