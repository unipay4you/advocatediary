from datetime import timedelta
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




class RegisterUser(APIView):
    def post(self, request):
        try:
            serializer =UserSerializer(data = request.data)
            if not serializer.is_valid():
                print(serializer.errors)
                return Response({
                    'status' : 403, 
                    'error': serializer.errors
                    })    
            
            serializer.save()

            user = CustomUser.objects.get(phone_number = serializer.data['phone_number'])
            refresh = RefreshToken.for_user(user)

            return Response({'status' : 200, 'data' : {'massage' : 'User registration Successfully. Verify with otp for login' , 'refresh_token': str(refresh),'access_token': str(refresh.access_token)}})
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})    

class UpdateUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            print(request.user)
            print(request.data)

            request_id = request.data['id']
            user_profile_image = request.data['user_profile_image']
            phone_number = str(request.data['phone_number'])
            email = request.data['email']
            user_name = request.data['user_name']
            user_dob = request.data['user_dob']
            user_address1 = request.data['user_address1']
            user_address2 = request.data['user_address2']
            user_address3 = request.data['user_address3']
            user_district_pincode = request.data['user_district_pincode']
            advocate_registration_number = request.data['advocate_registration_number']
            user_state = request.data['user_state']
            user_district = request.data['user_district']

            user_obj = CustomUser.objects.get(id = request_id)
            state_obj = State.objects.get(id = user_state)
            district_obj = District.objects.get(id = user_district)
            updation_validation = True

            print(user_obj.phone_number)
            if user_obj.phone_number != phone_number:
                updation_validation = False
                return Response({'status' : 404,'error' : 'phone_number not match with user'})

            print(user_obj.email)
            print(email)
            print(CustomUser.objects.filter(email = email).exists())
            if user_obj.email != email and CustomUser.objects.filter(email = email).exists():
                updation_validation = False
                return Response({'status' : 404,'error' : 'Email already exist'})

            print(updation_validation)
            if updation_validation:
                user_obj.user_name = user_name
                user_obj.user_dob = user_dob
                user_obj.user_address1 = user_address1
                user_obj.user_address2 = user_address2
                user_obj.user_address3 = user_address3
                user_obj.user_district_pincode = user_district_pincode
                user_obj.advocate_registration_number = advocate_registration_number
                user_obj.user_state = state_obj
                user_obj.user_district = district_obj
                user_obj.is_first_login = False

                if user_obj.email != email:
                    user_obj.email = email
                    user_obj.is_email_verified = False 

                if user_profile_image != "":
                    user_obj.user_profile_image = user_profile_image

                user_obj.save()
                return Response({'status' : 200, 'massage' : 'Profile updated'})
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

            user_obj = CustomUser.objects.get(phone_number = user)
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
            
            
            if (user_obj.otp != request.data['otp']) or time_diff > 300:
                return Response({'status' : 403, 'message' : 'OTP not match or Expired'})
            user_obj.is_phone_number_verified = True
            user_obj.save()
            return Response({'status' : 200, 'message' : 'OTP Verify successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'}) 
    

class resendOTP(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            if user != request.data['phone_number']:
                return Response({'status' : 401, 'message' : 'Requested token does not match with user'})

            user_obj = CustomUser.objects.get(phone_number = user)
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
           
            
            if time_diff < 30:
                return Response({'status' : 403, 'message' : 'resend otp after 30 sec of previous otp send'})
            
            otp = random.randint(100001, 999999)
            otp = 123456
            user_obj.otp = otp
            
            user_obj.otp_created_at = datetime.now(timezone.utc)
            
            user_obj.save()
            return Response({'status' : 200, 'message' : 'OTP Resend successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class resendEmail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            
            user_obj = CustomUser.objects.get(phone_number = user)
            
            email_token = uuid4()
            
            user_obj.email_token = email_token
            user_obj.email_token_created_at = datetime.now(timezone.utc)
            user_obj.save()

            send_email_token(user_obj.email, email_token)
            return Response({'status' : 200, 'message' : 'Email send successfully, check your email'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class ChangeEmail(APIView):
    def post(self, request):  # sourcery skip: extract-method, inline-variable
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        
        try:
            user = str(request.user)
            new_email = request.data['new_email']
            print(user)
            user_obj = CustomUser.objects.filter(email = new_email)
            if not user_obj.exists():

                user_obj = CustomUser.objects.get(phone_number = user)


                email_token = uuid4()
                
                user_obj.email = new_email
                user_obj.email_token = email_token
                user_obj.email_token_created_at = datetime.now(timezone.utc)
                user_obj.save()

                send_email_token(user_obj.email, email_token)
                return Response({'status' : 200, 'message' : 'Email send successfully, check your email'})
            else:
                return Response({'status' : 402, 'message' : 'Email already exist'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class Login(APIView):
    def post(self, request):
        try:
            user = request.data['phone_number']
            password = request.data['password']
            

            user_obj = CustomUser.objects.filter(phone_number = user)
            if not user_obj.exists():
                return Response({'status' : 401, 'message' : 'User not exist...'})

            user_obj = authenticate(phone_number = user, password = password)
            if user_obj is None:
                return Response({'status' : 402, 'message' : 'Mobile number and password not match'})
            
            
            refresh = RefreshToken.for_user(user_obj)
            otp = random.randint(100001, 999999)
            otp = 123456
            otp_msg = f'Hi, {user} Welcome back. Your Login OTP is {otp}'

            
            user_obj.otp = otp
            user_obj.otp_created_at = datetime.now(timezone.utc)
            user_obj.save()

            send_msg_to_mobile(user, otp, otp_msg)
            

            return Response({'status' : 200, 'data' : {'massage' : 'User Login Successfully.' , 'refresh_token': str(refresh),'access_token': str(refresh.access_token)}})


        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        


class CaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request):
        try:
            user = request.user
            case_obj = Case_Master.objects.filter(advocate = user, is_active = True).order_by('next_date')
            user_obj = CustomUser.objects.filter(phone_number = user)
            
            caseserializer = CaseSerializer(case_obj, many=True)
            userserializer = ProfileSerializer(user_obj, many=True)

            total_case = len(case_obj)
            today_cases = len(case_obj.filter(next_date = datetime.now().date()))
            tommarow_cases  = len(case_obj.filter(next_date = datetime.now().date()+timedelta(1)))
            date_awaited_case = len(case_obj.filter(next_date__lt = datetime.now().date()))

            print(total_case)
            print(today_cases)
            print(today_cases)
            print(tommarow_cases)
            print(date_awaited_case)

            return Response({'status' : 200, 
                             'userData': userserializer.data, 
                             'cases' : caseserializer.data, 
                             'count' : {
                                 'total_case' : total_case, 
                                 'today_cases' : today_cases,
                                 'tommarow_cases' : tommarow_cases,
                                 'date_awaited_case' : date_awaited_case
                                 }})
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        user_obj = CustomUser.objects.filter(phone_number = user)
        serializer = ProfileSerializer(user_obj, many=True)
        return Response({'status' : 200, 'payload' : serializer.data})


class getDistrict(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    




































class GeneratePDF(APIView):
    def get(self, request):


        return Response({'status' : 200})




class Case_API(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pass
       

    def post(self, request):
        print(request.user)
        
        case_obj = CustomUser.objects.all()
        serializer = CaseSerializer(case_obj, many=True)
        return Response({'status' : 200, 'payload' : serializer.data})

    def put(self, request):
        pass

    def patch(self, request):
        pass

    def delete(self, request):
        pass



    

@api_view(['POST'])
def Court(request):
    data = request.data
    serializer = CourtSerializer(data = data)

    if not serializer.is_valid():
        print(serializer.errors)
        return Response({'status' : 403, 'error': serializer.errors, 'message' : 'Something went wrong'})    

    serializer.save()
    
    return Response({'status' : 200, 'payload' : serializer.data})
