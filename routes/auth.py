
from flask import (
    Blueprint, request, session,
    render_template, redirect, url_for
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from models import db, Farmer

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# Farmer Registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    # Check empty fields
    if not name or not email or not password or not confirm_password:
        return render_template(
            'register.html',
            error='All fields are required'
        ), 400

    # Check password length
    if len(password) < 8:
        return render_template(
            'register.html',
            error='Password must contain at least 8 characters'
        ), 400

    # Check password confirmation
    if password != confirm_password:
        return render_template(
            'register.html',
            error='Passwords do not match'
        ), 400

    # Check whether email already exists
    existing_farmer = Farmer.query.filter_by(email=email).first()

    if existing_farmer:
        return render_template(
            'register.html',
            error='Email already registered. Please login.'
        ), 409

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create new farmer
    new_farmer = Farmer(
        name=name,
        email=email,
        password=hashed_password
    )

    try:
        db.session.add(new_farmer)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return render_template(
            'register.html',
            error='Registration failed. Please try again.'
        ), 500

    return render_template(
        'login.html',
        success='Registration successful! Please login.'
    )


# Farmer Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    # Check empty fields
    if not email or not password:
        return render_template(
            'login.html',
            error='Email and password are required'
        ), 400

    # Find farmer in database
    farmer = Farmer.query.filter_by(email=email).first()

    # Verify password
    if not farmer or not check_password_hash(
        farmer.password, password
    ):
        return render_template(
            'login.html',
            error='Email or password is incorrect'
        ), 401

    # Store farmer details in session
    session.clear()
    session['farmer_id'] = farmer.id
    session['farmer_name'] = farmer.name

    return redirect(url_for('dashboard'))


# Farmer Logout
@auth_bp.route('/logout', methods=['POST'])
def logout():

    session.clear()

    return redirect(url_for('auth.login'))
