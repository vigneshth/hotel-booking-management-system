from flask import Flask, render_template, request, redirect, url_for, flash, session 
from db_manager import HotelDBManager
from db_setup import setup_database
import os
from datetime import date 
from functools import wraps 

app = Flask(__name__)
app.secret_key = 'your_super_secret_project_key'
db = HotelDBManager() 

# --- Setup Check ---
if not os.path.exists(db.db_name):
    print("Database file not found. Running setup...")
    setup_database()

# --- Access Control Decorator ---
def login_required(f):
    """Decorator to protect routes from unauthenticated access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Access Denied. Please log in to view this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Main/Base Routes ---

@app.route('/')
def index():
    hotels = db.get_all_hotels()
    return render_template('index.html', hotels=hotels)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.authenticate_user(username, password)
        
        if user:
            session['logged_in'] = True
            session['user_role'] = user['role_name']
            session['username'] = username
            
            flash(f"Login successful. Welcome, {user['role_name']}.", 'success')
            return redirect(url_for('hotels')) 
        else:
            error = 'Invalid Credentials.'
            return render_template('login.html', error=error)
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the user by clearing the session."""
    session.pop('logged_in', None)
    session.pop('user_role', None)
    session.pop('username', None)
    flash("You have been logged out.", 'success')
    return redirect(url_for('index'))

# --- Management/Read Routes ---

@app.route('/hotels')
@login_required 
def hotels():
    hotels_list = db.get_all_hotels()
    return render_template('hotels.html', hotels=hotels_list)

@app.route('/bookings')
@login_required 
def bookings():
    """Renders the booking summary report using the SQL VIEW."""
    booking_details = db.get_booking_summary_report()
    return render_template('bookings.html', bookings=booking_details)

@app.route('/customers')
@login_required 
def customers():
    """Renders the list of customers."""
    customers_list = db.get_all_customers()
    return render_template('customers.html', customers=customers_list) 

@app.route('/payments')
@login_required 
def payments():
    """Renders the list of payments."""
    payments_list = db.get_all_payments_detailed()
    return render_template('payments.html', payments=payments_list)

# --- Hotel CRUD Routes ---

@app.route('/add_hotel', methods=['GET', 'POST'])
@login_required 
def add_hotel():
    if request.method == 'POST':
        try:
            name = request.form['name']
            type = request.form['type']
            desc = request.form['desc']
            rent = float(request.form['rent'])
            manager_id = 1 
            
            if db.add_hotel(name, type, desc, rent, manager_id):
                flash('Hotel added successfully!', 'success')
                return redirect(url_for('hotels'))
            else:
                flash('Error adding hotel. Check if manager ID exists.', 'error')
        except ValueError:
            flash('Invalid input for rent.', 'error')
    
    return render_template('add_hotel.html')

@app.route('/edit_hotel/<int:hotl_id>', methods=['GET', 'POST'])
@login_required 
def edit_hotel(hotl_id):
    hotel = db.get_hotel_by_id(hotl_id)
    if not hotel:
        flash('Hotel not found.', 'error')
        return redirect(url_for('hotels'))

    if request.method == 'POST':
        try:
            name = request.form['hotl_name']
            type = request.form['hotl_type']
            desc = request.form['hotl_desc']
            rent = float(request.form['hotl_rent'])
            manager_id = int(request.form['hotl_manager_id'])
            
            if db.update_hotel(hotl_id, name, type, desc, rent, manager_id):
                flash(f'Hotel {name} updated successfully!', 'success')
                return redirect(url_for('hotels'))
            else:
                flash('Error updating hotel. Check input fields.', 'error')
        except Exception:
            flash('Update failed. Ensure all fields are valid.', 'error')
            
    return render_template('edit_hotel.html', hotel=hotel)

@app.route('/delete_hotel/<int:hotl_id>')
@login_required 
def delete_hotel(hotl_id):
    if db.delete_hotel(hotl_id):
        flash(f'Hotel ID {hotl_id} deleted successfully.', 'success')
    else:
        flash(f'Error deleting Hotel ID {hotl_id}. It may have active bookings/dependencies.', 'error')
    
    return redirect(url_for('hotels'))

# --- Booking CRUD Routes ---

@app.route('/add_booking', methods=['GET', 'POST'])
def add_booking():
    hotels_list = db.get_all_hotels()
    
    if request.method == 'POST':
        try:
            # STEP 1: Get data including customer details and payment
            customer_email = request.form['customer_email'] 
            customer_name = request.form['customer_name'] 
            customer_mobile = request.form['customer_mobile']
            customer_address = request.form['customer_address']
            hotl_id = int(request.form['hotl_id'])
            book_type = request.form['book_type']
            desc = request.form['book_desc']
            check_in = request.form['check_in_date']
            check_out = request.form['check_out_date']
            initial_payment = float(request.form.get('initial_payment') or 0) 
            
            # STEP 2: Find the Customer ID
            cus_id = db.get_customer_id_by_email(customer_email)
            
            # --- FIX: If customer not found, create a full new record ---
            if cus_id is None:
                # Use the new method to create a complete customer record
                success = db.create_customer_full(
                    customer_name, customer_mobile, customer_email, None, customer_address
                ) 
                
                if success:
                    # Retrieve the newly created ID for booking
                    cus_id = db.get_customer_id_by_email(customer_email) 
                    flash(f'New customer "{customer_name}" registered successfully.', 'info')
                else:
                    flash('Error registering new customer.', 'error')
                    return render_template('add_booking.html', hotels=hotels_list)
            # -------------------------------------------------------------

            # STEP 3 & 4: Create Booking and Payment
            if db.add_booking(cus_id, hotl_id, book_type, desc, check_in, check_out):
                
                if initial_payment > 0:
                    today = date.today().isoformat()
                    pay_desc = f"Deposit for booking at {hotl_id}"
                    db.add_payment(cus_id, initial_payment, today, pay_desc)
                    flash('Booking created successfully! Initial payment recorded.', 'success')
                else:
                    flash('Booking created successfully!', 'success')
                
                return redirect(url_for('index'))
            else:
                flash('Error creating booking. Check hotel details.', 'error')
                
        except ValueError:
             flash('Invalid input: Hotel ID or Payment must be valid numbers.', 'error')
        except Exception as e:
             print(f"Booking Submission Error: {e}")
             flash('An unexpected error occurred during submission.', 'error')
             
    return render_template('add_booking.html', hotels=hotels_list)

@app.route('/edit_booking/<int:book_id>', methods=['GET', 'POST'])
@login_required 
def edit_booking(book_id):
    booking = db.get_booking_by_id_detailed(book_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('bookings'))

    if request.method == 'POST':
        hotl_id = request.form['book_hotel_id']
        book_type = request.form['book_type']
        desc = request.form['book_desc']
        
        if db.update_booking(book_id, hotl_id, book_type, desc):
            flash(f'Booking {book_id} updated successfully!', 'success')
            return redirect(url_for('bookings'))
        else:
            flash('Error updating booking.', 'error')

    return render_template('edit_booking.html', booking=booking)


# --- Customer CRUD Routes ---

@app.route('/delete_customer/<int:cus_id>')
@login_required 
def delete_customer(cus_id):
    if db.delete_customer(cus_id):
        flash(f'Customer ID {cus_id} deleted successfully.', 'success')
    else:
        flash(f'Error: Customer ID {cus_id} could not be deleted. Check for active bookings/payments.', 'error')
    
    return redirect(url_for('customers'))

@app.route('/edit_customer/<int:cus_id>', methods=['GET', 'POST'])
@login_required 
def edit_customer(cus_id):
    customer = db.get_customer_by_id(cus_id)
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('customers'))

    if request.method == 'POST':
        name = request.form['cus_name']
        mobile = request.form['cus_mobile']
        email = request.form['cus_email']
        address = request.form['cus_add']
        
        if db.update_customer(cus_id, name, mobile, email, address):
            flash(f'Customer {name} updated successfully!', 'success')
            return redirect(url_for('customers'))
        else:
            flash('Error updating customer.', 'error')
            
    return render_template('edit_customer.html', customer=customer)


# --- Payment CRUD Routes ---

@app.route('/delete_payment/<int:pay_id>')
@login_required 
def delete_payment(pay_id):
    if db.delete_payment(pay_id):
        flash(f'Payment ID {pay_id} deleted successfully.', 'success')
    else:
        flash(f'Error deleting Payment ID {pay_id}.', 'error')
    
    return redirect(url_for('payments')) 

@app.route('/add_payment', methods=['GET', 'POST'])
@login_required 
def add_payment():
    if request.method == 'POST':
        try:
            cus_id = int(request.form['cus_id'])
            amount = float(request.form['pay_amt'])
            date_str = request.form['pay_date']
            desc = request.form['pay_desc']
            
            if db.add_payment(cus_id, amount, date_str, desc):
                flash('Payment recorded successfully!', 'success')
                return redirect(url_for('payments'))
            else:
                flash('Error recording payment. Check Customer ID.', 'error')
        except Exception:
            flash('Invalid input.', 'error')

    return render_template('add_payment.html', today=date.today().isoformat())

@app.route('/edit_payment/<int:pay_id>', methods=['GET', 'POST'])
@login_required 
def edit_payment(pay_id):
    payment = db.get_payment_by_id(pay_id)
    if not payment:
        flash('Payment not found.', 'error')
        return redirect(url_for('payments'))

    if request.method == 'POST':
        try:
            cus_id = int(request.form['pay_cus_id'])
            amount = float(request.form['pay_amt'])
            date_str = request.form['pay_date']
            desc = request.form['pay_desc']
            
            if db.update_payment(pay_id, cus_id, amount, date_str, desc):
                flash(f'Payment {pay_id} updated successfully!', 'success')
                return redirect(url_for('payments'))
            else:
                flash('Error updating payment. Check Customer ID.', 'error')
        except Exception:
            flash('Invalid input.', 'error')

    return render_template('edit_payment.html', payment=payment)


if __name__ == '__main__':
    app.run(debug=True)