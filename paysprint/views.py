from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from jcikotastar.models import *
from django.contrib.messages import constants as messages
from django.contrib import messages
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
import random
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from rest_framework.views import APIView
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max,Min,Q, Count, F, Sum, Avg
from django.core.files.base import ContentFile
import base64
from django.contrib.auth.hashers import make_password, check_password
from paysprint.jwt import *
import requests

logger = logging.getLogger(__name__)
logger = logging.getLogger('django')



class TestView(APIView):
    def get(self, request):
        try:
            jwtToken = get_jwt_secret_key_live()


            operator = 81
            canumber = 210731004241


            url = "https://api.paysprint.in/api/v1/service/bill-payment/bill/fetchbill"

            payload = "{\"operator\":81,\"canumber\":210731004241,\"mode\":\"online\"}"
            
            headers = {
                "accept": "application/json",
                "Token": jwtToken,
                
                "content-type": "application/json"
            }

            response = requests.post(url, data=payload, headers=headers)

            print(response.text)



            return Response({'status' : 200,'jwt_key' : jwtToken, 'data' : response.json()})
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})