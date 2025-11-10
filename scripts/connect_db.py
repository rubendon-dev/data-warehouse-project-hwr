import psycopg2

# --- 1. Hardcoded Connection Parameters ---
DB_HOST = 'localhost' #SHOW listen_addresses;
DB_NAME = 'cocoa'
DB_USER = 'hdaphne'  #SELECT current_user;
DB_PASS = ''  # Use your actual password, or '' if using the Postgres.app default
DB_PORT = 5435  # use SHOW port; in postgreSQL to see what port you use.

TABLE_NAME = 'cocoa_yields'
CSV_FILE_PATH = '../datasets/cocoa-bean-yields.csv'

# SQL to check if the table exists
SQL_CHECK_TABLE = f"""
SELECT EXISTS (
    SELECT FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename  = '{TABLE_NAME}'
);
"""

# SQL to create the table
SQL_CREATE_TABLE = f"""
CREATE TABLE {TABLE_NAME} (
    id SERIAL PRIMARY KEY,
    entity TEXT NOT NULL,
    code VARCHAR(8),
    year INTEGER,
    cocoa_beans REAL
);
"""

conn = None
cursor = None

try:
    # Establish connection
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("✅ Connection to PostgreSQL established.")

    # --- 2. Check Table Existence ---
    cursor.execute(SQL_CHECK_TABLE)
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        # --- A. Table Does NOT Exist (Create and Import) ---
        print(f"Table '{TABLE_NAME}' not found. Creating table...")

        # Create Table
        cursor.execute(SQL_CREATE_TABLE)
        conn.commit()
        print(f"Table '{TABLE_NAME}' created.")

        # Import Data
        print(f"Importing data from: {CSV_FILE_PATH}")
        with open(CSV_FILE_PATH, 'r') as f:
            cursor.copy_expert(
                f"""
                COPY {TABLE_NAME} (entity, code, year, cocoa_beans)
                FROM STDIN WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE)
                """,
                f
            )
        conn.commit()
        print("✅ Data imported successfully!")

    else:
        # --- B. Table Exists (Skip Creation/Import) ---
        print(f"Table '{TABLE_NAME}' already exists. Skipping import.")

    # --- 3. Count Rows (Final Step) ---
    print(f"Counting rows in '{TABLE_NAME}'...")
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
    row_count = cursor.fetchone()[0]
    print(f"📊 Total rows in '{TABLE_NAME}': {row_count}")

except psycopg2.Error as e:
    print(f"❌ Database error occurred: {e}")
    if conn:
        conn.rollback()
except FileNotFoundError:
    print(f"❌ Error: CSV file not found at path: {CSV_FILE_PATH}. Check your relative pathing.")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        print("Connection closed.")