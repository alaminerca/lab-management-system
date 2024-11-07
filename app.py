from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Test users
USERS = {
    '123': {'password': 'test123', 'role': 'administrator'},
    '456': {'password': 'test456', 'role': 'student'},
    '789': {'password': 'test789', 'role': 'it_staff'}
}


# Decorator for requiring login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Basic routes
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
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Lab Management Routes
@app.route('/labs/view')
@login_required
def view_labs():
    # Implement lab viewing logic
    return "View Labs Page - Coming Soon"


@app.route('/labs/book')
@login_required
def book_lab():
    if session['role'] not in ['student', 'instructor']:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return "Book Lab Page - Coming Soon"


@app.route('/labs/assign')
@login_required
def assign_lab():
    if session['role'] != 'administrator':
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return "Assign Lab Page - Coming Soon"


# Inventory Management Routes
@app.route('/inventory/request')
@login_required
def request_equipment():
    if session['role'] != 'administrator':
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return "Request Equipment Page - Coming Soon"


@app.route('/inventory/purchase')
@login_required
def purchase_equipment():
    if session['role'] != 'administrator':
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return "Purchase Equipment Page - Coming Soon"


# IT Staff Routes
@app.route('/maintenance/tasks')
@login_required
def maintenance_tasks():
    if session['role'] != 'it_staff':
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return "Maintenance Tasks Page - Coming Soon"


@app.route('/equipment/check')
@login_required
def check_equipment():
    if session['role'] != 'it_staff':
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return "Check Equipment Page - Coming Soon"


if __name__ == '__main__':
    app.run(debug=True)