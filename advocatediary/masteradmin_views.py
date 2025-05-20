from datetime import timedelta, time, datetime, date
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from v1.models import *
from api.serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from api.utils import *
from uuid import uuid4
from django.db import transaction
from django.db.models import Max,Min,Q, Count
from jcikotastar.models import *
from api.masteradminserializers import *




class SuperAdminDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = str(request.user)
            user_obj = CustomUser.objects.get(phone_number = user)

            if not user_obj.is_superuser:
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})

            advUser_obj = CustomUser.objects.all()
            advuserserializer = AdvocateSerializer_MasterAdmin(advUser_obj, many=True)

            cases_obj = Case_Master.objects.all()
            casesserializer = CaseSerializer(cases_obj, many=True)
            
            return Response({'status' : 200, 'advUser' : advuserserializer.data, 'cases' : casesserializer.data, 'message' : 'Success'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class SuperAdminCourtView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = str(request.user)
            
            court_obj = Court.objects.all()
            courtserializer = CourtSerializer(court_obj, many=True)

            return Response({'status' : 200, 'court' : courtserializer.data, 'message' : 'Success'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class SuperAdminVerifyOTPView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            
            user = str(request.data['user_id'])
            user_obj = CustomUser.objects.get(id = user)
            

            if not user_obj.is_superuser:
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            user_obj.is_phone_number_verified  = True
            user_obj.save()
            return Response({'status' : 200,'message' : 'Phone number verified successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class SuperAdminVerifyEmailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            
            user = str(request.data['user_id'])
            user_obj = CustomUser.objects.get(id = user)
            

            if not user_obj.is_superuser:
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            user_obj.is_email_verified  = True
            user_obj.save()
            return Response({'status' : 200,'message' : 'Email verified successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class SuperAdminToggleStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            
            user = str(request.data['user_id'])
            user_obj = CustomUser.objects.get(id = user)


            if not user_obj.is_superuser:
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            
            if user_obj.is_active:
                return Response({'status' : 200,'message' : 'User activated successfully'})
            else:
                return Response({'status' : 200,'message' : 'User deactivated successfully'})


        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class SuperAdminResetPasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            
            user = str(request.data['user_id'])
            user_obj = CustomUser.objects.get(id = user)


            if not user_obj.is_superuser:
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            

            new_password = str(random.randint(100000,999999))
            email = user_obj.email
            print(new_password)
            send_email_password(email, new_password)
            user_obj.password = make_password(new_password)
            user_obj.save()
            return Response({'status' : 200,'message' : 'Password reset successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        

class SuperAdminCourtAddView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            
            user = request.user
            user_obj = CustomUser.objects.get(phone_number = user)
            

            if not user_obj.is_superuser:
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            district_id = request.data['district_id']
            state_id = request.data['state_id']
            court_name = request.data['court_name']
            court_type = request.data['court_type']
            court_no = request.data['court_no']

            district_obj = District.objects.get(id = district_id)
            state_obj = State.objects.get(id = state_id)
            court_type_obj = Court_Type.objects.get(id = court_type)
            court_obj = Court.objects.create(
                court_name = court_name,
                court_type = court_type_obj,
                court_no = court_no,
                district = district_obj,
                state = state_obj
            )
            
            print(court_obj)
            return Response({'status' : 200,'message' : 'Court added successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})