import sqlite3
import os
import bcrypt

DB_NAME = 'hotel_booking.db'

# --- Hashing Helper ---
def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Hashed passwords for initial data
PASS1_HASHED = hash_password('pass1')
PASS2_HASHED = hash_password('pass2')

SQL_SCHEMA = """
-- ======================================
-- Create tables
-- ======================================
CREATE TABLE IF NOT EXISTS USER_TABLE ( user_id INTEGER PRIMARY KEY, user_name TEXT NOT NULL, user_mobile TEXT, user_email TEXT, user_address TEXT );
CREATE TABLE IF NOT EXISTS ROLES ( role_id INTEGER PRIMARY KEY, role_name TEXT NOT NULL, role_desc TEXT );
CREATE TABLE IF NOT EXISTS LOGIN ( login_id INTEGER PRIMARY KEY, login_role_id INTEGER NOT NULL, login_username TEXT NOT NULL UNIQUE, user_password TEXT NOT NULL, FOREIGN KEY (login_role_id) REFERENCES ROLES(role_id) );
CREATE TABLE IF NOT EXISTS PERMISSION ( per_id INTEGER PRIMARY KEY, per_role_id INTEGER NOT NULL, per_name TEXT NOT NULL, per_module TEXT, FOREIGN KEY (per_role_id) REFERENCES ROLES(role_id) );
CREATE TABLE IF NOT EXISTS CUSTOMER ( cus_id INTEGER PRIMARY KEY, cus_name TEXT NOT NULL, cus_mobile TEXT, cus_email TEXT, cus_pass TEXT NOT NULL, cus_add TEXT );
CREATE TABLE IF NOT EXISTS HOTEL ( hotl_id INTEGER PRIMARY KEY, hotl_type TEXT, hotl_desc TEXT, hotl_name TEXT NOT NULL, hotl_rent REAL, hotl_manager_id INTEGER, FOREIGN KEY (hotl_manager_id) REFERENCES USER_TABLE(user_id) );
CREATE TABLE IF NOT EXISTS BOOKING ( book_id INTEGER PRIMARY KEY, book_desc TEXT, book_type TEXT, book_cus_id INTEGER NOT NULL, book_hotel_id INTEGER NOT NULL, book_check_in TEXT, book_check_out TEXT, FOREIGN KEY (book_cus_id) REFERENCES CUSTOMER(cus_id), FOREIGN KEY (book_hotel_id) REFERENCES HOTEL(hotl_id) );
CREATE TABLE IF NOT EXISTS PAYMENTS ( pay_id INTEGER PRIMARY KEY, pay_cus_id INTEGER NOT NULL, pay_amt REAL NOT NULL, pay_date TEXT, pay_desc TEXT, FOREIGN KEY (pay_cus_id) REFERENCES CUSTOMER(cus_id) );
"""

SQL_VIEW = """
-- ======================================
-- CORRECTED Database VIEW for reporting
-- Includes Customer Mobile and Address
-- ======================================
CREATE VIEW IF NOT EXISTS BookingSummary AS
SELECT 
    B.book_id,
    C.cus_name AS Customer_Name,
    C.cus_mobile AS Customer_Mobile,  -- NEW FIELD
    C.cus_add AS Customer_Address,    -- NEW FIELD
    H.hotl_name AS Hotel_Name,
    B.book_type AS Room_Type,
    H.hotl_rent AS Room_Rent,
    P.pay_amt AS Payment_Amount,
    P.pay_date AS Payment_Date
FROM BOOKING B
JOIN CUSTOMER C ON B.book_cus_id = C.cus_id 
JOIN HOTEL H ON B.book_hotel_id = H.hotl_id   
LEFT JOIN PAYMENTS P ON B.book_cus_id = P.pay_cus_id 
ORDER BY B.book_id;
"""

SQL_INSERT_DATA = [
    # USER_TABLE
    "INSERT INTO USER_TABLE VALUES (1, 'Alice', '9876543210', 'alice@email.com', 'Address 1');",
    "INSERT INTO USER_TABLE VALUES (2, 'Bob', '9876543211', 'bob@email.com', 'Address 2');",
    # ROLES
    "INSERT INTO ROLES VALUES (1, 'Admin', 'Full system access');",
    "INSERT INTO ROLES VALUES (2, 'Manager', 'Manage hotels and bookings');",
    # LOGIN - USING HASHED PASSWORDS
    f"INSERT INTO LOGIN VALUES (1, 1, 'alice123', '{PASS1_HASHED}');",
    f"INSERT INTO LOGIN VALUES (2, 2, 'bob123', '{PASS2_HASHED}');",
    # PERMISSION (Subset)
    "INSERT INTO PERMISSION VALUES (1, 1, 'Full Access', 'All');",
    "INSERT INTO PERMISSION VALUES (2, 2, 'Manage Bookings', 'Bookings');",
    # CUSTOMER
    "INSERT INTO CUSTOMER VALUES (1, 'Tom', '9988776655', 'tom@email.com', 'tom123', 'Addr1');",
    "INSERT INTO CUSTOMER VALUES (2, 'Jerry', '9988776656', 'jerry@email.com', 'jerry123', 'Addr2');",
    # HOTEL
    "INSERT INTO HOTEL VALUES (1, '5-Star', 'Luxury hotel', 'Hotel A', 5000, 1);",
    "INSERT INTO HOTEL VALUES (2, '4-Star', 'Comfortable stay', 'Hotel B', 4000, 2);",
    # BOOKING (Added dummy dates)
    "INSERT INTO BOOKING VALUES (1, 'Single room booking', 'Single', 1, 1, '2025-10-01', '2025-10-05');",
    "INSERT INTO BOOKING VALUES (2, 'Double room booking', 'Double', 2, 2, '2025-10-02', '2025-10-06');",
    # PAYMENTS
    "INSERT INTO PAYMENTS VALUES (1, 1, 5000, '2025-10-01', 'Payment for booking 1');",
    "INSERT INTO PAYMENTS VALUES (2, 2, 4000, '2025-10-02', 'Payment for booking 2');"
]

def setup_database():
    """Initializes the SQLite database, creates tables, view, and inserts sample data."""
    try:
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
            print(f"🧹 Existing database '{DB_NAME}' removed.")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.executescript(SQL_SCHEMA)
        print("✅ Tables created successfully.")
        
        cursor.executescript(SQL_VIEW)
        print("✅ View 'BookingSummary' created successfully.")

        for statement in SQL_INSERT_DATA:
            cursor.execute(statement)
        
        conn.commit()
        print("✅ Sample data inserted successfully.")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    setup_database()