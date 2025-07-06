# ==============================================================================
# Email Sending Service
# ------------------------------------------------------------------------------
# This file handles all logic for sending emails, such as OTPs for
# verification and password resets.
# ==============================================================================

import traceback
from flask_mail import Message
from flask import current_app # Import current_app

# DO NOT import mail from app here. We will get it from the app context.

def send_otp_email(to_email, otp):
    """Sends an email with the OTP for verification."""
    try:
        # Get the initialized mail object from the current application context.
        mail = current_app.extensions.get('mail')
        if not mail:
            # This is a fallback check in case initialization failed.
            print("CRITICAL ERROR: Mail extension not found on current_app.")
            return False

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
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False

def send_password_reset_email(to_email, otp):
    """Sends an email with the OTP for password reset."""
    try:
        # Get the initialized mail object from the current application context.
        mail = current_app.extensions.get('mail')
        if not mail:
            print("CRITICAL ERROR: Mail extension not found on current_app.")
            return False

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
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False