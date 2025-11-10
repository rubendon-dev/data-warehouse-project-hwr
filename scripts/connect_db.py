import psycopg2

# --- 1. Your Connection Parameters ---
DB_HOST = 'localhost'  # Usually 'localhost' or '127.0.0.1' SHOW listen_addresses;
DB_NAME = 'cocoa'  # Your database name
DB_USER = 'hdaphne' #SELECT current_user;
DB_PASS = '' # if you use postgreSQl app, mac default password is empty ''.
DB_PORT = 5435  # use SHOW port; in postgreSQL to see what port you use.

# --- 2. Connection Logic ---
conn = None
try:
    # Attempt to establish the connection
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

    # If successful, create a cursor to execute SQL commands
    cursor = conn.cursor()
    print("✅ Connection to PostgreSQL successful!")

    # Example: Run a simple query
    cursor.execute("SELECT COUNT(*) FROM cocoa_yield;")
    record_count = cursor.fetchone()[0]
    print(f"Total rows in cocoa_yield table: {record_count}")

    # Commit the changes (not needed for SELECT, but good practice for INSERT/UPDATE)
    # conn.commit()

except psycopg2.Error as e:
    # Print any specific database errors
    print(f"❌ Database connection error: {e}")

finally:
    # --- 3. Close the Connection ---
    if conn:
        conn.close()
        print("Connection closed.")