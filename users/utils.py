import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import OTPToken


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user):
    # Delete any old unused OTPs for this user before creating new one
    OTPToken.objects.filter(user=user, is_used=False).delete()

    # Generate new OTP
    otp_code = generate_otp()

    # Set expiry to 5 minutes from now
    expires_at = timezone.now() + timedelta(minutes=5)

    # Save OTP to database
    OTPToken.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False
    )

    # Send email
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP is: {otp_code}\n\nThis code expires in 5 minutes. Do not share it with anyone.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_otp(user, otp_code):
    try:
        otp = OTPToken.objects.get(
            user=user,
            otp_code=otp_code,
            is_used=False
        )
    except OTPToken.DoesNotExist:
        return False, "Invalid OTP"

    # Check if expired
    if timezone.now() > otp.expires_at:
        return False, "OTP has expired"

    # Mark as used so it cannot be reused
    otp.is_used = True
    otp.save()

    return True, "OTP verified successfully"