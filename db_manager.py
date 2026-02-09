import sqlite3
import bcrypt

class HotelDBManager:
    """Manages all database interactions for the Hotel Booking System."""
    
    def __init__(self, db_name='hotel_booking.db'):
        self.db_name = db_name

    def _execute(self, query, params=(), fetch_one=False):
        """Internal method to handle connection, execution, and closing."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith(("SELECT", "PRAGMA", "WITH")):
                return cursor.fetchone() if fetch_one else cursor.fetchall()
            else:
                conn.commit()
                return True

        except sqlite3.Error as e:
            # Uncomment the line below temporarily if you need to debug a database error
            # print(f"Database Error: {e}") 
            if conn:
                conn.rollback()
            return False

        finally:
            if conn:
                conn.close()

    # --- Authentication ---
    def authenticate_user(self, username, password):
        query = "SELECT L.user_password, R.role_name FROM LOGIN L JOIN ROLES R ON L.login_role_id = R.role_id WHERE L.login_username = ?"
        user_record = self._execute(query, (username,), fetch_one=True)
        
        if user_record:
            hashed_password = user_record['user_password'].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return user_record 
        return None

    # --- Reporting ---
    def get_booking_summary_report(self):
        """Uses the corrected BookingSummary VIEW."""
        return self._execute("SELECT * FROM BookingSummary;")
    
    # --- Hotel CRUD Operations ---
    def get_all_hotels(self):
        return self._execute("SELECT hotl_id, hotl_name, hotl_type, hotl_rent, hotl_manager_id FROM HOTEL;")
    def get_hotel_by_id(self, hotel_id):
        return self._execute("SELECT * FROM HOTEL WHERE hotl_id = ?", (hotel_id,), fetch_one=True)
    def add_hotel(self, name, type, desc, rent, manager_id):
        query = "INSERT INTO HOTEL (hotl_name, hotl_type, hotl_desc, hotl_rent, hotl_manager_id) VALUES (?, ?, ?, ?, ?)"
        return self._execute(query, (name, type, desc, rent, manager_id))
    def update_hotel(self, hotel_id, name, type, desc, rent, manager_id):
        query = "UPDATE HOTEL SET hotl_name=?, hotl_type=?, hotl_desc=?, hotl_rent=?, hotl_manager_id=? WHERE hotl_id=?"
        return self._execute(query, (name, type, desc, rent, manager_id, hotel_id))
    def delete_hotel(self, hotel_id):
        return self._execute("DELETE FROM HOTEL WHERE hotl_id = ?", (hotel_id,))

    # --- Customer CRUD Operations ---
    def get_all_customers(self):
        return self._execute("SELECT cus_id, cus_name, cus_mobile, cus_email, cus_add FROM CUSTOMER;")
    
    def get_customer_id_by_email(self, email):
        """Retrieves customer ID based on email address."""
        query = "SELECT cus_id FROM CUSTOMER WHERE cus_email = ?"
        result = self._execute(query, (email,), fetch_one=True)
        return result['cus_id'] if result else None
    
    def create_customer_full(self, name, mobile, email, password, address):
        """Inserts a new customer with all fields (Used by add_booking)."""
        query = """
        INSERT INTO CUSTOMER (cus_name, cus_mobile, cus_email, cus_pass, cus_add) 
        VALUES (?, ?, ?, ?, ?);
        """
        default_pass = "temporary" 
        
        # NOTE: Using 'name' from the form, which may be None if not provided
        return self._execute(query, (name, mobile, email, default_pass, address))

    def delete_customer(self, cus_id):
        """Deletes a customer record. (Will fail on active FKs)."""
        query = "DELETE FROM CUSTOMER WHERE cus_id = ?"
        return self._execute(query, (cus_id,))
    
    def get_customer_by_id(self, cus_id):
        return self._execute("SELECT * FROM CUSTOMER WHERE cus_id = ?", (cus_id,), fetch_one=True)
    
    def update_customer(self, cus_id, name, mobile, email, address):
        query = "UPDATE CUSTOMER SET cus_name=?, cus_mobile=?, cus_email=?, cus_add=? WHERE cus_id=?"
        return self._execute(query, (name, mobile, email, address, cus_id))

    # --- Booking CRUD Operations ---
    def add_booking(self, cus_id, hotl_id, book_type, desc, check_in, check_out):
        query = "INSERT INTO BOOKING (book_cus_id, book_hotel_id, book_type, book_desc, book_check_in, book_check_out) VALUES (?, ?, ?, ?, ?, ?)"
        return self._execute(query, (cus_id, hotl_id, book_type, desc, check_in, check_out))
    def get_booking_by_id_detailed(self, book_id):
        query = "SELECT B.*, C.cus_name AS Customer_Name, H.hotl_name AS Hotel_Name FROM BOOKING B JOIN CUSTOMER C ON B.book_cus_id = C.cus_id JOIN HOTEL H ON B.book_hotel_id = H.hotl_id WHERE B.book_id = ?"
        return self._execute(query, (book_id,), fetch_one=True)
    def update_booking(self, book_id, hotl_id, book_type, desc):
        query = "UPDATE BOOKING SET book_hotel_id=?, book_type=?, book_desc=? WHERE book_id=?"
        return self._execute(query, (hotl_id, book_type, desc, book_id))
        
    # --- Payment CRUD Operations ---
    def delete_payment(self, pay_id):
        query = "DELETE FROM PAYMENTS WHERE pay_id = ?"
        return self._execute(query, (pay_id,))
    def get_all_payments_detailed(self):
        query = "SELECT P.*, C.cus_name AS Customer_Name FROM PAYMENTS P JOIN CUSTOMER C ON P.pay_cus_id = C.cus_id ORDER BY P.pay_date DESC"
        return self._execute(query)
    def get_payment_by_id(self, pay_id):
        return self._execute("SELECT * FROM PAYMENTS WHERE pay_id = ?", (pay_id,), fetch_one=True)
    def add_payment(self, cus_id, amount, date, desc):
        query = "INSERT INTO PAYMENTS (pay_cus_id, pay_amt, pay_date, pay_desc) VALUES (?, ?, ?, ?)"
        return self._execute(query, (cus_id, amount, date, desc))
    def update_payment(self, pay_id, cus_id, amount, date, desc):
        query = "UPDATE PAYMENTS SET pay_cus_id=?, pay_amt=?, pay_date=?, pay_desc=? WHERE pay_id=?"
        return self._execute(query, (cus_id, amount, date, desc, pay_id))