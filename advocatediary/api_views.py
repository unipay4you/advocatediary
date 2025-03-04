from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from v1.models import *
from api.serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken



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

            return Response({'status' : 200, 'massage' : 'User registration Successfully. Verify with otp for login' , 'refresh': str(refresh),'access': str(refresh.access_token)})
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
                return Response({'status' : 403, 'message' : 'Requested token does not match with user'})

            user_obj = CustomUser.objects.get(phone_number = user)
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
            if user_obj.is_phone_number_verified:
                return Response({'status' : 403, 'message' : 'OTP already verified'})
            
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
                return Response({'status' : 403, 'message' : 'Requested token does not match with user'})

            user_obj = CustomUser.objects.get(phone_number = user)
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
            if user_obj.is_phone_number_verified:
                return Response({'status' : 403, 'message' : 'OTP already verified'})
            
            if time_diff < 300:
                return Response({'status' : 403, 'message' : 'resend otp after 5 min of previous otp send'})
            
            user_obj.otp = random.randint(100001, 999999)
            user_obj.otp_created_at = datetime.now(timezone.utc)
            
            user_obj.save()
            return Response({'status' : 200, 'message' : 'OTP Resend successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})















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
