# ==============================================================================
# Authentication Routes
# ------------------------------------------------------------------------------
# This file handles the entire user authentication lifecycle, including:
#   - /register:         New user registration form.
#   - /verify:           Email OTP verification and initial password setting.
#   - /login:            Existing user login.
#   - /forgot-password:  Requesting a password reset.
#   - /reset-password:   Entering OTP and setting a new password.
# ==============================================================================

import random
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.services import firebase_service, leetcode_api, email_service

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('leetcode_username')
        email = request.form.get('email')

        # 1. Check if the username or email is already taken in our database
        if firebase_service.get_user_data(username) or firebase_service.get_user_by_email(email):
            flash('A user with that LeetCode username or email already exists.', 'error')
            return redirect(url_for('auth.register'))
        
        # 2. Check if the LeetCode user actually exists
        if not leetcode_api.get_user_stats(username):
            flash('This LeetCode username could not be found.', 'error')
            return redirect(url_for('auth.register'))

        # 3. Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # 4. CRUCIAL: Call the correct function to create an unverified user
        firebase_service.create_unverified_user(username, email, otp)
        
        # 5. Send the verification email
        email_service.send_otp_email(email, otp)
        
        # 6. Store the username in the session so the /verify route knows who is verifying
        session['verifying_username'] = username
        flash('A verification code has been sent to your email.', 'info')
        return redirect(url_for('auth.verify'))

    return render_template('register.html')


@bp.route('/verify', methods=['GET', 'POST'])
def verify():
    username = session.get('verifying_username')
    if not username:
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        otp = request.form.get('otp')
        password = request.form.get('password')
        
        user_data = firebase_service.get_user_data(username)
        # TODO: Add a check for OTP expiration
        if user_data and user_data.get('otp') == otp:
            password_hash = generate_password_hash(password)
            firebase_service.verify_user_and_set_password(username, password_hash)
            
            # Clean up the verification session key and log the user in
            session.pop('verifying_username', None)
            session['leetcode_username'] = username
            flash('Account verified successfully! You are now logged in.', 'success')
            return redirect(url_for('dashboard.user_dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = firebase_service.get_user_by_email(email)
        
        # Check if user exists, is verified, and if the password matches the stored hash
        if user_data and user_data.get('is_verified') and check_password_hash(user_data.get('password_hash', ''), password):
            session['leetcode_username'] = user_data['leetcode_username']
            return redirect(url_for('dashboard.user_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user_data = firebase_service.get_user_by_email(email)
        
        # We only do the backend work if the user actually exists.
        if user_data:
            username = user_data['leetcode_username']
            otp = str(random.randint(100000, 999999))
            firebase_service.set_password_reset_otp(username, otp)
            email_service.send_password_reset_email(email, otp)
        
        # We ALWAYS set the session key and flash the same message to avoid leaking information
        # and to prevent the redirect loop.
        session['resetting_email'] = email
        flash('If an account with that email exists, a password reset code has been sent.', 'info')
        return redirect(url_for('auth.reset_password'))
            
    return render_template('forgot_password.html')


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('resetting_email')
    if not email:
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        otp = request.form.get('otp')
        new_password = request.form.get('password')
        
        user_data = firebase_service.get_user_by_email(email)
        
        # TODO: Add a check for OTP expiration
        if user_data and user_data.get('reset_otp') == otp:
            new_password_hash = generate_password_hash(new_password)
            firebase_service.reset_password(user_data['leetcode_username'], new_password_hash)
            
            # Clean up the session and redirect to login
            session.pop('resetting_email', None)
            flash('Your password has been successfully reset. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            
    return render_template('reset_password.html')