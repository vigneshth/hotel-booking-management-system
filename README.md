# Hotel Booking and Management System

The Hotel Booking and Management System is a database-driven application designed to manage hotel operations efficiently, including users, roles, hotels, customer bookings, and payments. The system provides structured access control using role-based permissions and ensures secure handling of booking and payment transactions.

This project demonstrates strong DBMS concepts such as relational schema design, primary and foreign key relationships, normalization, and SQL queries, along with a basic backend layer and a simple web interface.

---

## System Overview

The system manages:
- Users and role-based access (RBAC)
- Hotels and hotel managers
- Customers and their bookings
- Payment records linked to customers and bookings

A centralized database ensures consistency, integrity, and efficient data retrieval.

---

## Entities and Description

- **User:** Staff or administrative users with attributes such as ID, name, mobile number, email, and address.
- **Login:** Stores authentication details including username, password, and role ID.
- **Roles:** Defines different user roles such as Admin, Manager, Receptionist, etc.
- **Permission:** Specifies actions allowed for each role (Role-Based Access Control).
- **Customer:** Guests who book hotels, including contact information and login credentials.
- **Hotel:** Hotel details including name, type, description, room rent, and assigned manager.
- **Booking:** Records customer bookings with booking type and description.
- **Payments:** Tracks payments made by customers, including amount, date, and description.

---

## Relationships

- Users can have multiple roles, and roles can be assigned to multiple users.
- Each hotel is managed by one user, while a user can manage multiple hotels.
- A customer can make multiple bookings, and a hotel can have multiple bookings.
- Roles determine permissions using an RBAC system.
- Customers can make multiple payments, usually associated with bookings.

---

## Relational Schema

### USER
- user_id (PK)
- user_name
- user_mobile
- user_email
- user_address

### LOGIN
- login_id (PK)
- login_role_id (FK → ROLES.role_id)
- login_username
- user_password

### ROLES
- role_id (PK)
- role_name
- role_desc

### PERMISSION
- per_id (PK)
- per_role_id (FK → ROLES.role_id)
- per_name
- per_module

### CUSTOMER
- cus_id (PK)
- cus_name
- cus_mobile
- cus_email
- cus_pass
- cus_add

### HOTEL
- hotl_id (PK)
- hotl_type
- hotl_desc
- hotl_name
- hotl_rent
- hotl_manager_id (FK → USER.user_id)

### BOOKING
- book_id (PK)
- book_desc
- book_type
- book_cus_id (FK → CUSTOMER.cus_id)
- book_hotel_id (FK → HOTEL.hotl_id)

### PAYMENTS
- pay_id (PK)
- pay_cus_id (FK → CUSTOMER.cus_id)
- pay_amt
- pay_date
- pay_desc

---

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python (basic backend logic)
- SQL

### Database
- Relational Database Management System (DBMS)
- SQL for table creation, constraints, and queries

---

## Key Highlights

- Well-structured relational database schema
- Role-Based Access Control (RBAC)
- Secure handling of bookings and payments
- Use of primary and foreign keys for data integrity
- Realistic sample data for testing
- Scalable and maintainable database design

---

## Conclusion

This project showcases the practical application of DBMS concepts in building a real-world hotel booking and management system. By organizing hotel operations, user access, bookings, and payments in a structured manner, the system improves efficiency, ensures data integrity, and demonstrates effective database-driven application design.

---

## Author

Madhu Vignesh R
