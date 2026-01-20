from jobdash_db.db_connection import get_connection
from jobdash_db.insights_SQL import INSIGHTS_SQL
from jobdash_db.transformation_SQL import TRANSFORMATION_SQL
from jobdash_db.views_SQL import VIEW_SQL

def split_sql(sql):
    return [s.strip() for s in sql.strip().split(";") if s.strip()]

def run_sql_block(cursor, sql_block):
    for stmt in split_sql(sql_block):
        cursor.execute(stmt)

def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        print("Running transformations...")
        for sql in TRANSFORMATION_SQL:
            run_sql_block(cursor, sql)

        print("Running views...")
        for sql in VIEW_SQL:
            run_sql_block(cursor, sql)

        conn.commit()
        print("SQL pipeline complete.")

        print("\nRunning insights:")
        for name, sql in INSIGHTS_SQL:
            cursor.execute(sql)
            rows = cursor.fetchall()
            print(f"\n{name}:")
            for row in rows[:10]:
                print(row)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
