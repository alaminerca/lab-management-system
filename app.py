from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from functools import wraps
from datetime import datetime, date
from modules.lab_management import LabManagement
from modules.equipment_management import EquipmentManagement

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Update the USERS dictionary in app.py
USERS = {
    '123': {
        'password': 'test123',
        'role': 'administrator',
        'name': 'Admin User',
        'permissions': [
            'view_lab',
            'assign_lab',
            'request_equipment',
            'purchase_equipment',
            'check_equipment',
            'view_maintenance_reports',
            'report_issue'  # Added permission
        ]
    },
    '456': {
        'password': 'test456',
        'role': 'student',
        'name': 'Student User',
        'permissions': [
            'view_lab',
            'book_lab',
            'access_lab',
            'report_issue'  # Added permission
        ]
    },
    '321': {
        'password': 'test321',
        'role': 'instructor',
        'name': 'Instructor User',
        'permissions': [
            'view_lab',
            'book_lab',
            'access_lab',
            'report_issue'  # Added permission
        ]
    },
    '789': {
        'password': 'test789',
        'role': 'it_staff',
        'name': 'IT Staff User',
        'permissions': [
            'maintain_equipment',
            'add_equipment',
            'remove_equipment',
            'check_equipment',
            'view_maintenance_reports',
            'report_issue'
        ]
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

    try:
        labs = LabManagement.get_all_labs()
        if not labs:  # If no labs are found
            flash('No labs are currently available in the system')

        current_time = datetime.now()
        return render_template(
            'labs/view.html',
            labs=labs,  # Will be an empty list if no labs found
            current_time=current_time,
            today=date.today().isoformat()
        )
    except Exception as e:
        print(f"Error in view_labs: {e}")
        flash('An error occurred while retrieving labs')
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/labs/book', methods=['GET', 'POST'])
@login_required
def book_lab():
    if 'book_lab' not in session.get('permissions', []):
        flash('You do not have permission to book labs')
        return redirect(url_for('view_labs'))

    if request.method == 'POST':
        try:
            lab_id = request.form.get('lab_id')
            booking_date = request.form.get('date')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')

            if not all([lab_id, booking_date, start_time, end_time]):
                flash('All fields are required')
                return redirect(url_for('view_labs'))

            try:
                start_datetime = datetime.strptime(f"{booking_date} {start_time}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{booking_date} {end_time}", "%Y-%m-%d %H:%M")

                # Check if booking is in the past
                if start_datetime < datetime.now():
                    flash('Cannot book labs in the past')
                    return redirect(url_for('view_labs'))

            except ValueError:
                flash('Invalid date or time format')
                return redirect(url_for('view_labs'))

            # Check lab availability
            if not LabManagement.is_lab_available(lab_id, start_datetime, end_datetime):
                flash('Lab is not available for the selected time slot')
                return redirect(url_for('view_labs'))

            # Create booking
            if LabManagement.book_lab(session['user_id'], lab_id, start_datetime, end_datetime):
                flash(f'Lab {lab_id} booked successfully for {booking_date} from {start_time} to {end_time}')
            else:
                flash('Failed to book lab')

            return redirect(url_for('view_labs'))

        except Exception as e:
            print(f"Error in book_lab: {str(e)}")
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

    bookings = LabManagement.get_user_bookings(session['user_id'])

    def is_current_booking(booking):
        now = datetime.now()
        start_time = datetime.strptime(booking['start_time'], '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(booking['end_time'], '%Y-%m-%d %H:%M')
        return start_time <= now <= end_time

    return render_template('labs/mybookings.html',
                           bookings=bookings,
                           is_current_booking=is_current_booking)


@app.route('/labs/access/<int:booking_id>')
@login_required
def access_lab(booking_id):
    if 'access_lab' not in session.get('permissions', []):
        flash('You do not have permission to access labs')
        return redirect(url_for('my_bookings'))

    booking = LabManagement.get_booking(booking_id)

    if not booking:
        flash('Booking not found')
        return redirect(url_for('my_bookings'))

    if booking['status'] != 'approved':
        flash('Booking must be approved to access lab')
        return redirect(url_for('my_bookings'))

    # Fix datetime string parsing
    current_time = datetime.now()
    start_time = datetime.strptime(booking['start_time'][:16], '%Y-%m-%d %H:%M')  # Remove seconds
    end_time = datetime.strptime(booking['end_time'][:16], '%Y-%m-%d %H:%M')  # Remove seconds

    if not (start_time <= current_time <= end_time):
        flash('Lab can only be accessed during booked time slot')
        return redirect(url_for('my_bookings'))

    return render_template('labs/access.html', booking=booking)


@app.route('/dashboard')
@login_required
def dashboard():
    current_active_booking = None
    if 'access_lab' in session.get('permissions', []):
        current_active_booking = LabManagement.get_current_active_booking(session['user_id'])
    return render_template('dashboard.html', current_active_booking=current_active_booking)


# Equipment section

@app.route('/equipment/check')
@login_required
def check_equipment():  # This is the correct function name
    if 'check_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    equipment_list = EquipmentManagement.get_all_equipment()
    return render_template('equipment/check.html', equipment=equipment_list)



@app.route('/equipment/report/<int:equip_id>', methods=['POST'])
@login_required
def report_issue(equip_id):
    # Changed from 'check_equipment' to 'report_issue'
    if 'report_issue' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    issue = request.form.get('issue')
    user_id = session['user_id']

    print(f"Reporting issue:")  # Debug prints
    print(f"Equipment ID: {equip_id}")
    print(f"Issue: {issue}")
    print(f"Reported by: {user_id}")

    if EquipmentManagement.report_issue(equip_id, issue, user_id):
        flash('Issue reported successfully')
    else:
        flash('Failed to report issue')

    return redirect(url_for('check_equipment'))


@app.route('/maintenance/tasks')
@login_required
def view_tasks():
    if 'maintain_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    # Get all maintenance tasks (reported issues)
    tasks = EquipmentManagement.get_maintenance_tasks()
    return render_template('maintenance/tasks.html', tasks=tasks)


@app.route('/equipment')
@login_required
def equipment_dashboard():
    if session.role == 'administrator':
        return redirect(url_for('inventory_status'))
    elif session.role == 'it_staff':
        return redirect(url_for('check_equipment'))
    else:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

@app.route('/labs')
@login_required
def labs_dashboard():
    if 'view_lab' in session.get('permissions', []):
        return redirect(url_for('view_labs'))
    flash('Unauthorized access')
    return redirect(url_for('dashboard'))

@app.route('/equipment/maintain', methods=['GET', 'POST'])
@login_required
def maintain_equipment():
    if 'maintain_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        task_id = request.form.get('task_id')
        resolution = request.form.get('resolution')

        if EquipmentManagement.resolve_maintenance(task_id, resolution, session['user_id']):
            flash('Maintenance completed successfully')
        else:
            flash('Failed to complete maintenance')
        return redirect(url_for('view_tasks'))

    # Get task details if task_id provided
    task_id = request.args.get('task_id')
    task = None
    if task_id:
        task = EquipmentManagement.get_maintenance_task(task_id)

    return render_template('equipment/maintain.html', task=task)


@app.route('/equipment/maintain/<int:issue_id>', methods=['POST'])
@login_required
def resolve_issue(issue_id):
    if 'maintain_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    resolution = request.form.get('resolution')
    if EquipmentManagement.resolve_issue(issue_id, resolution, session['user_id']):
        flash('Issue resolved successfully')
    else:
        flash('Failed to resolve issue')
    return redirect(url_for('maintain_equipment'))


@app.route('/inventory/request', methods=['GET', 'POST'])
@login_required
def request_from_inventory():
    if 'request_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        equip_type = request.form.get('equipment_type')
        quantity = request.form.get('quantity')
        reason = request.form.get('reason')

        # Simulate inventory check (in real system, this would be an API call)
        response = EquipmentManagement.check_inventory(equip_type, quantity)

        if response['available']:
            flash(f'Equipment available. IT Staff will be notified to add {quantity} {equip_type}(s).')
        else:
            flash('Equipment not available in inventory. Consider purchase request.')

        return redirect(url_for('inventory_status'))

    return render_template('inventory/request.html')


@app.route('/inventory/purchase', methods=['GET', 'POST'])
@login_required
def purchase_equipment():
    if 'purchase_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        equip_type = request.form.get('equipment_type')
        quantity = request.form.get('quantity')
        justification = request.form.get('justification')

        if EquipmentManagement.submit_purchase_request(equip_type, quantity, justification, session['user_id']):
            flash('Purchase request submitted successfully')
        else:
            flash('Failed to submit purchase request')
        return redirect(url_for('inventory_status'))

    return render_template('inventory/purchase.html')


@app.route('/inventory/purchase/<int:request_id>/<string:action>', methods=['POST'])
@login_required
def process_purchase(request_id, action):
    if 'purchase_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    if action == 'delivered':
        EquipmentManagement.mark_purchase_delivered(request_id)
        flash('Equipment delivered from inventory')

    return redirect(url_for('inventory_status'))


@app.route('/inventory/status')
@login_required
def inventory_status():
    if 'request_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    requests = EquipmentManagement.get_inventory_requests(session['user_id'])
    return render_template('inventory/status.html', requests=requests)


@app.route('/equipment/add')
@login_required
def add_equipment():
    if 'add_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    # Get pending requests from inventory
    pending_requests = EquipmentManagement.get_pending_inventory_requests()
    return render_template('equipment/add.html', pending_requests=pending_requests)


@app.route('/equipment/add/<int:request_id>', methods=['POST'])
@login_required
def confirm_add_equipment(request_id):
    if 'add_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    if EquipmentManagement.add_equipment_from_request(request_id):
        flash('Equipment added successfully')
    else:
        flash('Failed to add equipment')

    return redirect(url_for('add_equipment'))


@app.route('/equipment/remove')
@login_required
def remove_equipment():
    if 'remove_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    equipment_list = EquipmentManagement.get_all_equipment()
    return render_template('equipment/remove.html', equipment=equipment_list)


@app.route('/equipment/remove/<int:equip_id>', methods=['POST'])
@login_required
def confirm_remove_equipment(equip_id):
    if 'remove_equipment' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    reason = request.form.get('reason')
    if EquipmentManagement.remove_equipment(equip_id, reason, session['user_id']):
        flash('Equipment removed successfully')
    else:
        flash('Failed to remove equipment')
    return redirect(url_for('remove_equipment'))


@app.route('/maintenance/reports')
@login_required
def maintenance_reports():
    if 'view_maintenance_reports' not in session.get('permissions', []):
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    maintenance_history = EquipmentManagement.get_maintenance_history()
    return render_template('maintenance/reports.html', history=maintenance_history)

if __name__ == '__main__':
    app.run(debug=True)
