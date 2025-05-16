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
from jcikotastar.helper import *
from rest_framework.permissions import IsAuthenticated
from jcikotastar.serializers import *
from django.db.models import Max,Min,Q, Count, F, Sum, Avg
from django.core.files.base import ContentFile
import base64
from django.contrib.auth.hashers import make_password, check_password

logger = logging.getLogger(__name__)
logger = logging.getLogger('django')


class LoginView(APIView):
    def post(self, request):
        try:
            user = request.data['phone_number']
            
            password = request.data['password']
            is_authonthicate = False
            
            #user_obj = CustomUser_JKS.objects.filter(phone_number = user)
            try:
                user_obj = CustomUser_JKS.objects.get(phone_number = user)
            except CustomUser_JKS.DoesNotExist:
                return Response({'status' : 401, 'message' : 'User not exist...'})

            if check_password(password, user_obj.password):
                print('password match')
                is_authonthicate = True  # authentication successful
            else:
                return Response({'status' : 402, 'message' : 'Mobile number and password not match'})
            
            
            refresh = RefreshToken.for_user(user_obj)
            otp = generate_otp()
            otp_msg = f'Hi, {user} Welcome back. Your Login OTP is {otp}'

            
            user_obj.otp = otp
            user_obj.otp_created_at = datetime.now(timezone.utc)
            user_obj.save()

            send_msg_to_mobile(user, otp, otp_msg)

            return Response({'status' : 200, 'data' : {'massage' : 'User Login Successfully.' , 'refresh_token': str(refresh),'access_token': str(refresh.access_token)}})
            

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class verifyOTP(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            user_json = str(request.data['phone_number'])
           
            if user != user_json:
                return Response({'status' : 401, 'message' : 'Requested token does not match with user'})

            user_obj = CustomUser_JKS.objects.get(phone_number = user)
            is_first_login = user_obj.is_first_login
            usertype = user_obj.user_type
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
            
            
            if (user_obj.otp != request.data['otp']) or time_diff > 300:
                return Response({'status' : 403, 'message' : 'OTP not match or Expired'})
            user_obj.is_phone_number_verified = True
            user_obj.save()
            return Response({'status' : 200, 'message' : 'OTP Verify successfully', 'data' : {'is_first_login' : is_first_login, 'usertype' : usertype}})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class verifyForgatePasswordOTP(APIView):
    def post(self, request):
        try:
            user = str(request.data['phone_number'])
           
            
            user_obj = CustomUser_JKS.objects.get(phone_number = user)
            is_first_login = user_obj.is_first_login
            usertype = user_obj.user_type
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
            
            
            if (user_obj.otp != request.data['otp']) or time_diff > 300:
                return Response({'status' : 403, 'message' : 'OTP not match or Expired'})
            refresh = RefreshToken.for_user(user_obj)
            user_obj.is_phone_number_verified = True
            user_obj.save()
            return Response({'status' : 200, 'message' : 'OTP Verify successfully','access_token' : str(refresh.access_token) ,'data' : {'is_first_login' : is_first_login, 'usertype' : usertype}})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class resendOTP(APIView):
    
    def post(self, request):
        try:
            user = str(request.data['phone_number'])
            
            user_obj = CustomUser_JKS.objects.filter(phone_number = user)

            if not user_obj.exists():
                return Response({'status' : 401, 'message' : 'User not exist...'})

            user_obj = CustomUser_JKS.objects.get(phone_number = user)
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
           
            
            if time_diff < 30:
                return Response({'status' : 403, 'message' : 'resend otp after 30 sec of previous otp send'})
            
            otp = generate_otp()
            user_obj.otp = otp
            otp_msg = f'Hi, {user} Welcome back. Your Login OTP is {otp}'
            send_msg_to_mobile(user, otp, otp_msg)
            user_obj.otp_created_at = datetime.now(timezone.utc)
            
            user_obj.save()
            return Response({'status' : 200, 'message' : 'OTP Resend successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        

class ChangePassword(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            
            user_obj = CustomUser_JKS.objects.get(phone_number = user)
            
            password = request.data['password']
            confirm_password = request.data['confirm_password']

            usertype = user_obj.user_type

            if password != confirm_password:
                return Response({'status' : 401, 'message' : 'Password and Confirm Password not match'})
            
            user_obj.password = make_password(password)
            #user_obj.set_password(password)
            user_obj.is_first_login = False
            user_obj.save()
            return Response({'status' : 200, 'message' : 'password changed successfully', 'data' : {'usertype' : usertype}})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        user_obj = CustomUser_JKS.objects.filter(phone_number = user)
        serializer = ProfileSerializer(user_obj, many=True)
        return Response({'status' : 200, 'payload' : serializer.data})
    
class ForgatPassword(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            
            user_obj = CustomUser_JKS.objects.get(phone_number = user)
            
            
            password = request.data['password']
            confirm_password = request.data['confirm_password']

            usertype = user_obj.user_type

            if password != confirm_password:
                return Response({'status' : 401, 'message' : 'Password and Confirm Password not match'})
            
            print(user)
            print(password)
            #user_obj.set_password(password)
            user_obj.password = make_password(password)
            user_obj.is_first_login = False
            user_obj.save()
            return Response({'status' : 200, 'message' : 'password changed successfully', 'data' : {'usertype' : usertype}})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class AddNewMembter(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
            user = str(request.user)
            jcName = request.data['jcName']
            jcMobile = request.data['jcMobile']
            jcrtName = request.data['jcrtName']
            jcrtMobile = request.data['jcrtMobile']
            anniversaryDate = request.data['anniversaryDate']
            jcDob = request.data['jcDob']
            jcrtDob = request.data['jcrtDob']
            jcQualification = request.data['jcQualification']
            jcBloodGroup = request.data['jcBloodGroup']
            jcEmail = request.data['jcEmail']
            jcHomeAddress = request.data['jcHomeAddress']
            jcOccupation = request.data['jcOccupation']
            jcFirmName = request.data['jcFirmName']
            jcOccupationAddress = request.data['jcOccupationAddress']
            jcrtBloodGroup = request.data['jcrtBloodGroup']
            jcrtEmail = request.data['jcrtEmail']
            jcrtOccupation = request.data['jcrtOccupation']
            jcrtOccupationAddress = request.data['jcrtOccupationAddress']
            jcpost = request.data['jcPost']
            jcrtpost = request.data['jcrtPost']
            jcImage = request.data['jcImage']
            jcrtImage = request.data['jcrtImage']
            searchteg = request.data['searchteg']
            print(jcpost)
            print(jcDob)
            print(jcrtDob)
            print(anniversaryDate)

            if (CustomUser_JKS.objects.filter(
                Q(phone_number = jcMobile) | Q(phone_number = jcrtMobile)
                ).exists()):
                return Response({'status' : 401, 'message' : 'User already exist...'})

            if jcpost in ['President', 'Secretary', 'Treasurer']:
                user_type = 'admin'
            else:
                user_type = 'member'

            user_obj_jc = CustomUser_JKS.objects.create(
                phone_number = jcMobile,
                user_profile_image = jcImage,
                email = jcEmail,
                user_type = user_type,
                user_name = jcName,
                user_dob = jcDob,
                is_phone_number_verified = False,
                is_first_login = True,
                mobile_number_belongs_to = 'JC',
                password = make_password(jcMobile),
            )
            #user_obj_jc.set_password(jcMobile)
            user_obj_jc.save()

            if jcrtMobile != '':
                user_obj_jcrt = CustomUser_JKS.objects.create(
                    phone_number = jcrtMobile,
                    user_profile_image = jcrtImage,
                    email = jcrtEmail,
                    user_type = user_type,
                    user_name = jcrtName,
                    user_dob = jcrtDob,
                    is_phone_number_verified = False,
                    is_first_login = True,
                    mobile_number_belongs_to = 'JCRT',
                    password = make_password(jcrtMobile),
                )
                #user_obj_jcrt.set_password(jcrtMobile)
                user_obj_jcrt.save()
            else:
                user_obj_jcrt = None

            user_detail_obj = UserDetail_JKS.objects.create(
                jcName = jcName,
                jcMobile = user_obj_jc,
                jcrtName = jcrtName,
                jcrtMobile = user_obj_jcrt,
                anniversaryDate = anniversaryDate,
                jcDob = jcDob,
                jcrtDob = jcrtDob,
                jcQualification = jcQualification,
                jcBloodGroup = jcBloodGroup,
                jcEmail = jcEmail,
                jcHomeAddress = jcHomeAddress,
                jcOccupation = jcOccupation,
                jcFirmName = jcFirmName,
                jcOccupationAddress = jcOccupationAddress,
                jcrtBloodGroup = jcrtBloodGroup,
                jcrtEmail = jcrtEmail,
                jcrtOccupation = jcrtOccupation,
                jcrtOccupationAddress = jcrtOccupationAddress,
                jcpost = jcpost,
                jcrtpost = jcrtpost,
                jcImage = jcImage,
                jcrtImage = jcrtImage,
                searchteg = searchteg
            )




            return Response({'status' : 200, 'message' : 'Add Member successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = str(request.user)
            user_obj = CustomUser_JKS.objects.get(phone_number = user)
            mobile_number_belongs_to = user_obj.mobile_number_belongs_to

            members_obj = UserDetail_JKS.objects.filter(is_active = True).order_by('jcName')

            if mobile_number_belongs_to == 'JCRT':
                user_detail_obj = UserDetail_JKS.objects.get(jcrtMobile = user_obj)
            else:
                user_detail_obj = UserDetail_JKS.objects.get(jcMobile = user_obj)
            
            prog_obj = ProgramName_JKS.objects.filter(prog_expire_date__gte = datetime.now(timezone.utc)).order_by('prog_start_date')

            profileserializer = ProfileSerializer(user_obj, many=False)
            userserializer = UserDetailSerializer(user_detail_obj, many=False)
            membersserializer = UserDetailSerializer(members_obj, many=True)
            programserializer = ProgramNameSerializer(prog_obj, many=True)

            return Response({'status' : 200, 'profile' : profileserializer.data, 'user' : userserializer.data, 'members' : membersserializer.data, 'programs' : programserializer.data})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class UpdateProfile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
           
            user = str(request.user)
            jcName = request.data['jcName']
            jcMobile = request.data['jcMobile']
            jcrtName = request.data['jcrtName']
            jcrtMobile = request.data['jcrtMobile']
            anniversaryDate = request.data['anniversaryDate']
            jcDob = request.data['jcDob']
            jcrtDob = request.data['jcrtDob']
            jcQualification = request.data['jcQualification']
            jcBloodGroup = request.data['jcBloodGroup']
            jcEmail = request.data['jcEmail']
            jcHomeAddress = request.data['jcHomeAddress']
            jcOccupation = request.data['jcOccupation']
            jcFirmName = request.data['jcFirmName']
            jcOccupationAddress = request.data['jcOccupationAddress']
            jcrtBloodGroup = request.data['jcrtBloodGroup']
            jcrtEmail = request.data['jcrtEmail']
            jcrtOccupation = request.data['jcrtOccupation']
            jcrtOccupationAddress = request.data['jcrtOccupationAddress']
            
            jcImage = request.data['jcImage']
            jcrtImage = request.data['jcrtImage']



            print(f'jcImage = {jcImage}')
            

            imageserializer = ImageSerializer(data=request.data)
            if imageserializer.is_valid():
                image_jc = imageserializer.validated_data['jcImage']
                image_jcrt = imageserializer.validated_data['jcrtImage']
            else:
                print(imageserializer.error_messages)
                
                
                
            print(f'jcImage = {image_jc}')
            print(f'jcrtImage = {image_jcrt}')                
            
            
            print(anniversaryDate)
            is_jcrt_user_created = False
            #check jcrt user exist or not as login user if not then create new user
            if not CustomUser_JKS.objects.filter(phone_number = jcrtMobile).exists():
                print('1')
                user_obj_jcrt = CustomUser_JKS.objects.create(
                    phone_number = jcrtMobile,
                    user_name = jcrtName,
                    is_phone_number_verified = False,
                    is_first_login = True,
                    mobile_number_belongs_to = 'JCRT',
                    user_profile_image = image_jcrt,
                    password = make_password(jcrtMobile),
                )
                #user_obj_jcrt.set_password(jcrtMobile)
                user_obj_jcrt.save()
                is_jcrt_user_created = True
            
            

            #get user object for update user profile
            user_obj = CustomUser_JKS.objects.get(phone_number = user)
            mobile_number_belongs_to = user_obj.mobile_number_belongs_to

            if mobile_number_belongs_to == 'JCRT':
                print('2')
                if image_jcrt != None:
                    user_obj.user_profile_image = image_jcrt
                
                user_obj.email = jcrtEmail
                user_obj.user_name = jcrtName
                user_obj.user_dob = jcrtDob
                mobile_number_belongs_to = 'JCRT'
            else:
                print('3')
                #check user detail profile availble or not if not aailable then create first
                if not UserDetail_JKS.objects.filter(jcMobile = user_obj).exists():
                    print('test')
                    user_detail_obj = UserDetail_JKS.objects.create(jcMobile = user_obj)
                    user_detail_obj.save()
                
                if image_jc != None:
                    print('jc')
                    user_obj.user_profile_image = image_jc
                user_obj.email = jcEmail
                user_obj.user_name = jcName
                user_obj.user_dob = jcDob
                user_obj.mobile_number_belongs_to = 'JC'
            print('4')
            user_obj.save()
            
            

            #get user detail object for update user detail profile
            if mobile_number_belongs_to == 'JCRT':
                user_detail_obj = UserDetail_JKS.objects.get(jcrtMobile = user_obj)
            else:
                user_detail_obj = UserDetail_JKS.objects.get(jcMobile = user_obj)

            print('5')
            user_detail_obj.anniversaryDate = anniversaryDate
            user_detail_obj.jcName = jcName
            user_detail_obj.jcDob = jcDob
            user_detail_obj.jcQualification = jcQualification
            user_detail_obj.jcEmail = jcEmail
            user_detail_obj.jcBloodGroup = jcBloodGroup
            user_detail_obj.jcHomeAddress = jcHomeAddress
            user_detail_obj.jcOccupation = jcOccupation
            user_detail_obj.jcFirmName = jcFirmName
            user_detail_obj.jcOccupationAddress = jcOccupationAddress
            
            if image_jc != None or image_jc == '':
                print('6')
                user_detail_obj.jcImage = image_jc
            
            if is_jcrt_user_created:
                print('7')
                user_detail_obj.jcrtMobile = user_obj_jcrt
            user_detail_obj.jcrtName = jcrtName
            user_detail_obj.jcrtDob = jcrtDob
            user_detail_obj.jcrtBloodGroup = jcrtBloodGroup
            user_detail_obj.jcrtEmail = jcrtEmail
            user_detail_obj.jcrtOccupation = jcrtOccupation
            user_detail_obj.jcrtOccupationAddress = jcrtOccupationAddress
            if image_jcrt != None or image_jcrt == '':
                print('8')
                user_detail_obj.jcrtImage = image_jcrt    
            
            user_detail_obj.save()    
            return Response({'status' : 200, 'message' : 'Profile Edit successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class ProgramImagesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
            year = request.data['year']
            queryset = ProgramImages_JKS.objects.filter(ProgramName__year = year)
            queryset2 = ProgramName_JKS.objects.filter(year = year)
            programimageserializer = ProgramImagesSerializer(queryset, many=True)
            programnameserializer = ProgramNameSerializer(queryset2, many=True)
            

            return Response({'status' : 200, 'payload' : programimageserializer.data, 'programs' : programnameserializer.data})
        

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        


class ProgramImagesByProgramIDView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
            program_id = request.data['program_id']
            
            queryset = ProgramImages_JKS.objects.filter(ProgramName__id = program_id)
            
            programnameserializer = ProgramImagesSerializer(queryset, many=True)
            

            return Response({'status' : 200, 'payload' : programnameserializer.data})
        

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class ImageUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
            
            program_id = request.data['program_id']
            image = request.data['image']
            

            if not ProgramName_JKS.objects.filter(id = program_id).exists():

                programName = request.data['programName']
                prog_year = request.data['year']
                
                ProgramName_obj = ProgramName_JKS.objects.create(programName = programName, year = prog_year)
                program_id = ProgramName_obj.id


            ProgramName_obj = ProgramName_JKS.objects.get(id = program_id)
            ProgramImages_JKS.objects.create(
                ProgramName = ProgramName_obj,
                image = image
                )
            return Response({'status' : 200, 'message' : 'Images upload successfully'})



        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        


class AdminDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = str(request.user)
            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if user_obj.user_type != 'admin':
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            
            members_obj = UserDetail_JKS.objects.all()

            
            profileserializer = ProfileSerializer(user_obj, many=False)
            membersserializer = UserDetailSerializer(members_obj, many=True)

            return Response({'status' : 200, 'profile' : profileserializer.data, 'members' : membersserializer.data})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class MembterChangeStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = str(request.user)
            member_id = request.data['member_id']

            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if user_obj.user_type != 'admin':
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            
            members_obj = UserDetail_JKS.objects.get(id = member_id)
            if members_obj.is_active == True:
                members_obj.is_active = False
                
            else:
                members_obj.is_active = True
                

            members_obj.save()
            

            
            return Response({'status' : 200, 'message' : 'Membter status changed successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class UpdateMembterProfileViewFromAdmin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
           
            user = str(request.user)
            member_id = request.data['member_id']
            print(member_id)
            jcName = request.data['jcName']
            jcMobile = request.data['jcMobile']
            jcrtName = request.data['jcrtName']
            jcrtMobile = request.data['jcrtMobile']
            anniversaryDate = request.data['anniversaryDate']
            jcDob = request.data['jcDob']
            jcrtDob = request.data['jcrtDob']
            jcQualification = request.data['jcQualification']
            jcBloodGroup = request.data['jcBloodGroup']
            jcEmail = request.data['jcEmail']
            jcHomeAddress = request.data['jcHomeAddress']
            jcOccupation = request.data['jcOccupation']
            jcFirmName = request.data['jcFirmName']
            jcOccupationAddress = request.data['jcOccupationAddress']
            jcrtBloodGroup = request.data['jcrtBloodGroup']
            jcrtEmail = request.data['jcrtEmail']
            jcrtOccupation = request.data['jcrtOccupation']
            jcrtOccupationAddress = request.data['jcrtOccupationAddress']
            jcpost = request.data['jcpost']
            jcrtpost = request.data['jcrtpost']
            
            jcImage = request.data['jcImage']
            jcrtImage = request.data['jcrtImage']

            print(jcpost)
            print(jcrtpost)

            

            imageserializer = ImageSerializer(data=request.data)
            if imageserializer.is_valid():
                image_jc = imageserializer.validated_data['jcImage']
                image_jcrt = imageserializer.validated_data['jcrtImage']
            else:
                print(imageserializer.error_messages)
            
            print(f'jcImage = {image_jc}')
            print(f'jcrtImage = {image_jcrt}')
                
                
            user_detail_obj = UserDetail_JKS.objects.get(id = member_id)

            if user_detail_obj.jcrtMobile == None:
                if jcrtMobile != '':
                    user_obj_jcrt = CustomUser_JKS.objects.create(
                        phone_number = jcrtMobile,
                        user_profile_image = image_jcrt,
                        email = jcrtEmail,
                        user_name = jcrtName,
                        user_dob = jcrtDob,
                        is_phone_number_verified = False,
                        is_first_login = True,
                        mobile_number_belongs_to = 'JCRT',
                        password = make_password(jcrtMobile),
                    )
                    #user_obj_jcrt.set_password(jcrtMobile)
                    user_obj_jcrt.save()

                    user_detail_obj.jcrtMobile = user_obj_jcrt
                else:
                    user_obj_jcrt = None

            
            


            user_detail_obj.anniversaryDate = anniversaryDate
            user_detail_obj.jcName = jcName
            user_detail_obj.jcDob = jcDob
            user_detail_obj.jcQualification = jcQualification
            user_detail_obj.jcEmail = jcEmail
            user_detail_obj.jcBloodGroup = jcBloodGroup
            user_detail_obj.jcHomeAddress = jcHomeAddress
            user_detail_obj.jcOccupation = jcOccupation
            user_detail_obj.jcFirmName = jcFirmName
            user_detail_obj.jcOccupationAddress = jcOccupationAddress
            user_detail_obj.jcpost = jcpost
            if image_jc != None or image_jc == '':
                user_detail_obj.jcImage = image_jc
            
            
            user_detail_obj.jcrtName = jcrtName
            user_detail_obj.jcrtDob = jcrtDob
            user_detail_obj.jcrtBloodGroup = jcrtBloodGroup
            user_detail_obj.jcrtEmail = jcrtEmail
            user_detail_obj.jcrtOccupation = jcrtOccupation
            user_detail_obj.jcrtOccupationAddress = jcrtOccupationAddress
            user_detail_obj.jcrtpost = jcrtpost
            if image_jcrt != None or image_jcrt == '':
                user_detail_obj.jcrtImage = image_jcrt    
            
            user_detail_obj.save()    
            return Response({'status' : 200, 'message' : 'Profile Edit successfully'})

        except Exception as e:
            error = str(e)
            if 'UNIQUE constraint failed' in error:
                return Response({'status' : 401, 'message' : 'Mobile number already exist...'})
            if 'NOT NULL constraint failed' in error:
                return Response({'status' : 402, 'message' : 'Please fill all required fields'})
            


class AdminMemberListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = str(request.user)
            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if user_obj.user_type != 'admin':
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            
            members_obj = UserDetail_JKS.objects.all()

            profileserializer = ProfileSerializer(user_obj, many=False)
            membersserializer = UserDetailSerializer(members_obj, many=True)

            return Response({'status' : 200, 'profile' : profileserializer.data, 'members' : membersserializer.data})
            

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class MembterUpdatePostView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = str(request.user)
            member_id = request.data['member_id']
            new_post = request.data['new_post']

            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            print(user)
            print(user_obj.user_type)
            print(new_post)
            if user_obj.user_type != 'admin':
                print('test')
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            
            members_obj = UserDetail_JKS.objects.get(id = member_id)
            members_obj.jcpost = new_post
            user_obj = CustomUser_JKS.objects.get(phone_number = members_obj.jcMobile.phone_number)
            if new_post == 'President' or new_post == 'Secretary' or new_post == 'Treasurer':
                
                user_obj.user_type = 'admin'
            else:
                user_obj.user_type = 'member'
                

            members_obj.save()
            user_obj.save()
            

            
            return Response({'status' : 200, 'message' : 'Membter status changed successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        

class MakeAdminView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = str(request.user)
            member_id = request.data['member_id']
            is_admin = request.data['is_admin']

            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if user_obj.user_type != 'admin':
                print('test')
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            
            members_obj = UserDetail_JKS.objects.get(id = member_id)
            user_obj = CustomUser_JKS.objects.get(phone_number = members_obj.jcMobile.phone_number)
            if is_admin == True:
                user_obj.user_type = 'admin'
            else:
                user_obj.user_type = 'member'
                
            user_obj.save()
            return Response({'status' : 200, 'message' : 'Membter status changed successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class AdminProgramView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = str(request.user)
            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if user_obj.user_type != 'admin':
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            
            
            program_obj = ProgramName_JKS.objects.all()

            programserializer = ProgramNameSerializer(program_obj, many=True)

            return Response({'status' : 200, 'programs' : programserializer.data})
            

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class ProgramEditView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
            user = str(request.user)
            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if user_obj.user_type != 'admin':
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            

            programName = request.data['programName']
            year = request.data['year']
            image = request.data['image']
            prog_expire_date = request.data['prog_expire_date']
            prog_start_date = request.data['prog_start_date']
            program_id = request.data['program_id']
            change_image = request.data['change_image']
           

            
            queryset = ProgramName_JKS.objects.get(id = program_id)

            
            
            imageserializer = ImageSerializer2(data=request.data)
            if imageserializer.is_valid():
                image = imageserializer.validated_data['image']
            else:
                print(imageserializer.error_messages)

            print(f'Image = {image}')

            queryset.programName = programName
            queryset.year = year
            if image != None or image == '':
                queryset.prog_image = image
            queryset.prog_expire_date = prog_expire_date
            queryset.prog_start_date = prog_start_date
            queryset.save()

            return Response({'status' : 200, 'message' : "Program updated successfully"})
        

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        
class ProgramAddView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
            user = str(request.user)
            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if user_obj.user_type != 'admin':
                return Response({'status' : 401, 'message' : 'You are not authorized to access this page'})
            

            programName = request.data['programName']
            year = request.data['year']
            image = request.data['image']
            prog_expire_date = request.data['prog_expire_date']
            prog_start_date = request.data['prog_start_date']

            imageserializer = ImageSerializer2(data=request.data)
            if imageserializer.is_valid():
                image = imageserializer.validated_data['image']
            else:
                print(imageserializer.error_messages)

            print(f'Image = {image}')
            
            queryset = ProgramName_JKS.objects.create(
                programName = programName,
                year = year,
                prog_image = image,
                prog_expire_date = prog_expire_date,
                prog_start_date = prog_start_date
                )
                
            return Response({'status' : 200, 'message' : "Program updated successfully"})
        

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class MembersProgramView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            program_obj = ProgramName_JKS.objects.all()

            programserializer = ProgramNameSerializer(program_obj, many=True)

            return Response({'status' : 200, 'programs' : programserializer.data})
            

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class GreetingCardsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = str(request.user)

            greetingcard_obj = UserGreeting_JKS.objects.filter(user__phone_number = user)
            greetingcardserializer = UserGreetingSerializer(greetingcard_obj, many=True)
            
            
            return Response({'status' : 200, 'payload' : greetingcardserializer.data})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class AddGreetingCardsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            image = ""
            greeting_image_type = request.data['greeting_image_type'].lower()
            print(greeting_image_type)
            print(image)
            imageserializer = ImageSerializer2(data=request.data)

            if imageserializer.is_valid():
                image = imageserializer.validated_data['image']
            else:
                print(imageserializer.error_messages)

            print(f'Image = {image}')

            user_obj = CustomUser_JKS.objects.get(phone_number = user)

            if UserGreeting_JKS.objects.filter(user__phone_number = user, greeting_image_type = greeting_image_type).exists():
                if image != None or image == '':
                    greeting_obj = UserGreeting_JKS.objects.get(user__phone_number = user, greeting_image_type = greeting_image_type)
                    #print(greeting_obj.greeting_image)
                    #print(image)
                    greeting_obj.greeting_image = image
                    #print(greeting_obj.greeting_image)
                    greeting_obj.save()

            else:
                if image != None or image == '':
                    UserGreeting_JKS.objects.create(
                        user = user_obj,
                        greeting_image = image,
                        greeting_image_type = greeting_image_type
                    )

            
            return Response({'status' : 200, 'message' : 'Greeting card added successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})