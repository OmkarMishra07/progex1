# app/services/email_service.py
import traceback
from flask_mail import Message
from flask import current_app # <--- Import current_app

# We will get the mail object from the app context, not the global scope
# from app import mail  <--- DELETE OR COMMENT OUT THIS LINE

def send_otp_email(to_email, otp):
    """Sends an email with the OTP for verification."""
    # Get the mail object from the currently running app
    mail = current_app.extensions.get('mail')
    if not mail:
        print("!!!!!!!! Mail extension not found on current_app. Check your __init__.py !!!!!!!!!!")
        return False
        
    try:
        msg = Message(
            'Your Progex Verification Code',
            recipients=[to_email],
            sender=current_app.config['MAIL_DEFAULT_SENDER'] # Explicitly set sender
        )
        msg.body = f'Your verification code for Progex is: {otp}\n\nThis code will expire in 10 minutes.'
        mail.send(msg)
        print(f"Successfully sent verification email to {to_email}")
        return True
    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"FAILED TO SEND VERIFICATION EMAIL to {to_email}")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR DETAILS: {e}")
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False

def send_password_reset_email(to_email, otp):
    """Sends an email with the OTP for password reset."""
    # Get the mail object from the currently running app
    mail = current_app.extensions.get('mail')
    if not mail:
        print("!!!!!!!! Mail extension not found on current_app. Check your __init__.py !!!!!!!!!!")
        return False

    try:
        msg = Message(
            'Your Progex Password Reset Code',
            recipients=[to_email],
            sender=current_app.config['MAIL_DEFAULT_SENDER'] # Explicitly set sender
        )
        msg.body = f'Your password reset code for Progex is: {otp}\n\nThis code will expire in 10 minutes. If you did not request this, you can safely ignore this email.'
        mail.send(msg)
        print(f"Successfully sent password reset email to {to_email}")
        return True
    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"FAILED TO SEND PASSWORD RESET EMAIL to {to_email}")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR DETAILS: {e}")
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False