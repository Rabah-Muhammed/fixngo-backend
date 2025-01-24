#utils.py
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import random
from oauth2client import client
import urllib
import requests
import jwt

def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp_in_cache(email, otp):
    cache.set(email, otp, timeout=300)  # OTP is valid for 5 minutes

def get_otp_from_cache(email):
    return cache.get(email)

def send_otp_to_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"Your OTP is: {otp}. It is valid for 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def get_id_token_with_code_method_1(code):
    
    credentials = client.credentials_from_clientsecrets_and_code(
        'client_secret.json',
        ['email','profile'],
        code
    )
    print(credentials.id_token)
    return credentials.id_token

def get_id_token_with_code_method_2(code):
    token_endpoint = "https://oauth2.googleapis.com/token"
    payload = {
        'code': code,
        'client_id': '500698877294-jam712pdk43id3s0v5mg9k1ol2jjdl6a.apps.googleusercontent.com',
        'client_secret': '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',
        'grant_type': 'authorization_code',
        'redirect_uri': "postmessage"
    }
    
    body = urllib.parse.urlencode(payload)
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(token_endpoint, data=body, headers=headers)
    if response.ok:
        id_token = response.json()['id_token']
        return jwt.decode(id_token, options={"verify_signature": False})
    else:
        print(response.json())
        return None