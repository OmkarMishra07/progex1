# ==============================================================================
# Email Sending Service
# ------------------------------------------------------------------------------
# This file handles all logic for sending emails, such as OTPs for
# verification and password resets.
# ==============================================================================

import traceback
from flask_mail import Message
from app import mail # Import the globally defined mail object
from flask import current_app

def send_otp_email(to_email, otp):
    """Sends an email with the OTP for verification."""
    try:
        # The `with mail.app.app_context()` block ensures that the email is sent
        # within the context of the fully configured Flask application.
        # This is the most reliable way to send emails with Flask-Mail.
        with mail.app.app_context():
            msg = Message(
                subject='Your Progex Verification Code',
                sender=('Progex', current_app.config['MAIL_DEFAULT_SENDER']),
                recipients=[to_email]
            )
            msg.body = f'Your verification code for Progex is: {otp}\n\nThis code will expire in 10 minutes.'
            
            mail.send(msg)
        
        print(f"INFO: Successfully processed send_otp_email for {to_email}")
        return True
    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR: FAILED TO SEND VERIFICATION EMAIL to {to_email}")
        traceback.print_exc() # Prints the full error for debugging
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False

def send_password_reset_email(to_email, otp):
    """Sends an email with the OTP for password reset."""
    try:
        # Using the same robust context block for this email function
        with mail.app.app_context():
            msg = Message(
                subject='Your Progex Password Reset Code',
                sender=('Progex', current_app.config['MAIL_DEFAULT_SENDER']),
                recipients=[to_email]
            )
            msg.body = f'Your password reset code for Progex is: {otp}\n\nThis code will expire in 10 minutes. If you did not request this, you can safely ignore this email.'
            
            mail.send(msg)
            
        print(f"INFO: Successfully processed send_password_reset_email for {to_email}")
        return True
    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR: FAILED TO SEND PASSWORD RESET EMAIL to {to_email}")
        traceback.print_exc() # Prints the full error for debugging
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False