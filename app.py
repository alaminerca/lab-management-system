from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from functools import wraps
from datetime import datetime, date
from modules.lab_management import LabManagement

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Updated users with all actors from use case
USERS = {
    '123': {
        'password': 'test123',
        'role': 'administrator',
        'name': 'Admin User',
        'permissions': ['view_lab', 'assign_lab', 'request_equipment', 'purchase_equipment']
    },
    '456': {
        'password': 'test456',
        'role': 'student',
        'name': 'Student User',
        'permissions': ['view_lab', 'book_lab', 'access_lab']
    },
    '321': {
        'password': 'test321',
        'role': 'instructor',
        'name': 'Instructor User',
        'permissions': ['view_lab', 'book_lab', 'access_lab']
    },
    '789': {
        'password': 'test789',
        'role': 'it_staff',
        'name': 'IT Staff User',
        'permissions': ['maintain_lab', 'add_equipment', 'remove_equipment', 'repair_equipment', 'check_equipment']
    }
}


# Decorator for requiring login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Route handlers
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        if user_id in USERS and USERS[user_id]['password'] == password:
            session['user_id'] = user_id
            session['role'] = USERS[user_id]['role']
            session['name'] = USERS[user_id]['name']
            session['permissions'] = USERS[user_id]['permissions']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')




@app.route('/labs/view')
@login_required
def view_labs():
    if 'view_lab' not in session.get('permissions', []):
        flash('You do not have permission to view labs')
        return redirect(url_for('dashboard'))

    labs = LabManagement.get_all_labs()
    return render_template('labs/view.html', labs=labs, today=date.today().isoformat())


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/labs/book', methods=['GET', 'POST'])
@login_required
def book_lab():
    print("Entering book_lab route")  # Debug print 1

    if 'book_lab' not in session.get('permissions', []):
        flash('You do not have permission to book labs')
        return redirect(url_for('view_labs'))

    if request.method == 'POST':
        print("POST request received")  # Debug print 2
        try:
            # Get form data
            lab_id = request.form.get('lab_id')
            booking_date = request.form.get('date')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')

            print(f"Form data received:")  # Debug print 3
            print(f"Lab ID: {lab_id}")
            print(f"Date: {booking_date}")
            print(f"Start Time: {start_time}")
            print(f"End Time: {end_time}")

            # Validate input
            if not all([lab_id, booking_date, start_time, end_time]):
                flash('All fields are required')
                return redirect(url_for('view_labs'))

            # Combine date and time
            try:
                start_datetime = datetime.strptime(f"{booking_date} {start_time}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{booking_date} {end_time}", "%Y-%m-%d %H:%M")
                print(f"Datetime conversion successful")  # Debug print 4
            except ValueError:
                flash('Invalid date or time format')
                return redirect(url_for('view_labs'))

            # Check lab availability
            is_available = LabManagement.is_lab_available(lab_id, start_datetime, end_datetime)
            print(f"Lab availability check: {is_available}")  # Debug print 5

            if not is_available:
                flash('Lab is not available for the selected time slot')
                return redirect(url_for('view_labs'))

            # Create booking
            booking_result = LabManagement.book_lab(session['user_id'], lab_id, start_datetime, end_datetime)
            print(f"Booking result: {booking_result}")  # Debug print 6

            if booking_result:
                flash(f'Lab {lab_id} booked successfully for {booking_date} from {start_time} to {end_time}')
                print("Success message flashed")  # Debug print 7
            else:
                flash('Failed to book lab')
                print("Failure message flashed")  # Debug print 8

            print("About to redirect")  # Debug print 9
            return redirect(url_for('view_labs'))

        except Exception as e:
            print(f"Error in book_lab: {str(e)}")  # Debug print 10
            flash('An error occurred while processing your booking')
            return redirect(url_for('view_labs'))

    return redirect(url_for('view_labs'))


@app.route('/labs/confirm', methods=['POST'])
@login_required
def confirm_booking():
    if 'book_lab' not in session.get('permissions', []):
        flash('You do not have permission to book labs')
        return redirect(url_for('view_labs'))

    try:
        # Get form data
        lab_id = request.form.get('lab_id')
        booking_date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        start_datetime = datetime.strptime(f"{booking_date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{booking_date} {end_time}", "%Y-%m-%d %H:%M")

        # Check if lab is available
        if not LabManagement.is_lab_available(lab_id, start_datetime, end_datetime):
            flash('Lab is not available for the selected time slot')
            return redirect(url_for('view_labs'))

        # Create booking
        booking_result = LabManagement.book_lab(session['user_id'], lab_id, start_datetime, end_datetime)

        if booking_result:
            flash(f'Lab {lab_id} booked successfully for {booking_date} from {start_time} to {end_time}')
        else:
            flash('Failed to book lab')

    except Exception as e:
        print(f"Error in confirm_booking: {str(e)}")
        flash('An error occurred while processing your booking')

    return redirect(url_for('view_labs'))


# In app.py, replace or add these routes:

@app.route('/labs/assignments')
@login_required
def view_assignments():
    if 'assign_lab' not in session.get('permissions', []):
        flash('You do not have permission to view assignments')
        return redirect(url_for('dashboard'))

    # Get all bookings with user and lab details
    bookings = LabManagement.get_all_bookings()
    return render_template('labs/assignments.html', bookings=bookings)


@app.route('/labs/assignment/process/<int:booking_id>/<string:action>', methods=['POST'])
@login_required
def process_lab_assignment(booking_id, action):  # Changed function name
    if 'assign_lab' not in session.get('permissions', []):
        flash('You do not have permission to assign labs')
        return redirect(url_for('view_assignments'))

    if action not in ['approve', 'reject']:
        flash('Invalid action')
        return redirect(url_for('view_assignments'))

    success = LabManagement.update_booking_status(booking_id, action)
    if success:
        flash(f'Booking {action}d successfully')
    else:
        flash(f'Failed to {action} booking')

    return redirect(url_for('view_assignments'))


@app.route('/labs/mybookings')
@login_required
def my_bookings():
    if not any(perm in session.get('permissions', []) for perm in ['book_lab', 'access_lab']):
        flash('You do not have permission to view bookings')
        return redirect(url_for('dashboard'))

    # Get bookings for current user
    bookings = LabManagement.get_user_bookings(session['user_id'])
    return render_template('labs/mybookings.html', bookings=bookings)



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)