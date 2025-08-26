# # your_app/utils.py
# import random
# from django.core.cache import cache
# from twilio.rest import Client
# from django.conf import settings
# from datetime import timedelta

# def generate_otp():
#     """Generate a random 6-digit OTP."""
#     return random.randint(100000, 999999)

# def store_otp(phone_number, otp):
#     """Store OTP in the cache with a 5-minute expiration."""
#     cache.set(f'otp_{phone_number}', otp, timeout=300)  # 5 minutes

# def send_otp(phone_number, otp):
#     """Send the OTP via SMS using Twilio."""
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#     message = client.messages.create(
#         body=f"Your OTP code is: {otp}",
#         from_=settings.TWILIO_PHONE_NUMBER,
#         to=phone_number
#     )
#     return message.sid  # Return the message SID if needed for logging
