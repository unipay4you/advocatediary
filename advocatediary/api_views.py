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

class verifyOTP(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            if user != request.data['phone_number']:
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
        user = request.user
        case_obj = Case_Master.objects.filter(advocate = user, is_active = True).order_by('next_date')
        user_obj = CustomUser.objects.filter(phone_number = user)
        print(user_obj)
        caseserializer = CaseSerializer(case_obj, many=True)
        userserializer = ProfileSerializer(user_obj, many=True)
        return Response({'status' : 200, 'data' : {'userData': userserializer.data, 'cases' : caseserializer.data}})
    



class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        user_obj = CustomUser.objects.filter(phone_number = user)
        serializer = ProfileSerializer(user_obj, many=True)
        return Response({'status' : 200, 'payload' : serializer.data})

class getDistrict(APIView):
    def get(self, request):
        district_obj = District.objects.all()
        serializer = DistrictSerializer(district_obj, many=True)
        return Response({'status' : 200, 'payload' : serializer.data})
    





































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
