import random
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render


def send_msg_to_mobile(mobile, otp, msg):
    try:
        print(msg)
    except Exception as e:
        print(e)
    


def send_email_token(email, email_token):
    try:
        address = [email,]
        subject = 'Your Account need to be verified'
        message = f'Click on the link to verify your email {settings.HOST_URL}/api/verify/{email_token}'
        obj = send_mail(subject, message, settings.EMAIL_HOST_USER, address)
        print('Mail send successfull')
    
    except Exception as e:
        print(e) 