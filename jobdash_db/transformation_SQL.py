# Normalize salary columns
normalize_columns = """
    ALTER TABLE merged_jobs
        ADD COLUMN salary_year_norm DOUBLE NULL,
        ADD COLUMN salary_hour_norm DOUBLE NULL,
        ADD COLUMN salary_norm_method VARCHAR(30) NULL,
        ADD COLUMN salary_is_outlier TINYINT(1) DEFAULT 0;
"""

# Populate normalized salary_columns
normalized_salary = """
    UPDATE merged_jobs
    SET
        salary_year_norm =
            CASE
                WHEN salary_year_avg IS NOT NULL THEN salary_year_avg
                WHEN min_salary IS NOT NULL AND max_salary IS NOT NULL THEN (min_salary + max_salary) / 2
                ELSE NULL
                END,

        salary_hour_norm =
            CASE
                WHEN salary_hour_avg IS NOT NULL THEN salary_hour_avg
                ELSE NULL
                END,

        salary_norm_method =
            CASE
                WHEN salary_year_avg IS NOT NULL THEN 'year_avg'
                WHEN min_salary IS NOT NULL AND max_salary IS NOT NULL THEN 'minmax_midpoint'
                WHEN salary_hour_avg IS NOT NULL THEN 'hour_avg_only'
                ELSE 'missing'
                END;
        """

# Outlier detection
outliers = """
   UPDATE merged_jobs
   SET salary_is_outlier =
           CASE
               WHEN (salary_hour_norm IS NOT NULL AND (salary_hour_norm < 5 OR salary_hour_norm > 500))
                   OR (salary_year_norm IS NOT NULL AND (salary_year_norm < 10000 OR salary_year_norm > 1000000))
                   THEN 1
               ELSE 0
               END;
"""


# Skills normalization
add_pkey = """
   ALTER TABLE merged_jobs
       ADD COLUMN job_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY;
"""

bridge_tables = """
    CREATE TABLE IF NOT EXISTS dim_skill (
         skill_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
         skill_name VARCHAR(255) NOT NULL,
         skill_name_norm VARCHAR(255) NOT NULL,
         UNIQUE KEY uq_skill_norm (skill_name_norm)
    );

    CREATE TABLE IF NOT EXISTS bridge_job_skill (
        job_id BIGINT UNSIGNED NOT NULL,
        skill_id BIGINT UNSIGNED NOT NULL,
        PRIMARY KEY (job_id, skill_id),
        KEY idx_skill_id (skill_id),
        CONSTRAINT fk_bjs_job FOREIGN KEY (job_id) REFERENCES merged_jobs(job_id),
        CONSTRAINT fk_bjs_skill FOREIGN KEY (skill_id) REFERENCES dim_skill(skill_id)
    );
"""

TRANSFORMATION_SQL = [
    normalize_columns,
    normalized_salary,
    outliers,
    add_pkey,
    bridge_tables,
]



# coverage report --> MOVE TO INSIGHTS
report = """
         SELECT
             COUNT(*) AS total_rows,
             SUM(salary_year_norm IS NOT NULL) AS year_norm_rows,
             SUM(salary_hour_norm IS NOT NULL) AS hour_norm_rows,
             SUM(salary_is_outlier = 1) AS outlier_rows
         FROM merged_jobs; \
         """












