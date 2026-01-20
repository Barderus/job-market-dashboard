from jobdash_db.db_connection import get_connection
from jobdash_db.insights_SQL import INSIGHTS_SQL
from jobdash_db.transformation_SQL import TRANSFORMATION_SQL
from jobdash_db.views_SQL import VIEWS_SQL

def split_sql(sql):
    return [s.strip() for s in sql.strip().split(";") if s.strip()]

def run_sql_block(cursor, sql_block):
    for stmt in split_sql(sql_block):
        cursor.execute(stmt)

def print_query_results(cursor, name, max_rows=10):
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    print(f"\n{name} ({len(rows)} rows)")
    print("-" * 80)

    # Header
    header = " | ".join(f"{col:<20}" for col in columns)
    print(header)
    print("-" * len(header))

    for row in rows[:max_rows]:
        print(" | ".join(f"{str(val):<20}" for val in row))

    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")

def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        print("Running transformations...")
        for sql in TRANSFORMATION_SQL:
            run_sql_block(cursor, sql)

        print("Running views...")
        for name, sql in VIEWS_SQL:
            run_sql_block(cursor, sql)


        conn.commit()
        print("SQL pipeline complete.")

        print("\nRunning insights:")
        for name, sql in INSIGHTS_SQL:
            try:
                cursor.execute(sql)
                print_query_results(cursor, name)
            except Exception as e:
                print(f"\n{name}: FAILED -> {e}")


    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
