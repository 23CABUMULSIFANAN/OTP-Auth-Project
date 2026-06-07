import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import OTPToken


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user):
    OTPToken.objects.filter(user=user, is_used=False).delete()

    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=5)

    OTPToken.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False
    )

    message = Mail(
        from_email=settings.EMAIL_HOST_USER,
        to_emails=user.email,
        subject='Your OTP Code',
        plain_text_content=f'Your OTP is: {otp_code}\n\nThis code expires in 5 minutes. Do not share it.'
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        print(f"OTP sent to {user.email}")
    except Exception as e:
        print(f"EMAIL FAILED: {str(e)}")
        raise


def verify_otp(user, otp_code):
    try:
        otp = OTPToken.objects.get(
            user=user,
            otp_code=otp_code,
            is_used=False
        )
    except OTPToken.DoesNotExist:
        return False, "Invalid OTP"

    if timezone.now() > otp.expires_at:
        return False, "OTP has expired"

    otp.is_used = True
    otp.save()

    return True, "OTP verified successfully"