from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_verification_otp_email(email, otp, user_name="User"):
    """
    Sends verification OTP to the user's email using HTML template
    """
    subject = "Your Verification OTP"
    from_email = "no-reply@pickey.com"
    to_email = [email]

    # Render HTML template with context
    html_content = render_to_string("emails/verification_otp.html", {
        "otp": otp,
        "user_name": user_name
    })

    # Create email
    email_message = EmailMultiAlternatives(subject=subject, body=html_content, from_email=from_email, to=to_email)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()
