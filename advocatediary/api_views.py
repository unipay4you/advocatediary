from datetime import timedelta, time, datetime, date
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
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
from django.contrib.auth.hashers import make_password, check_password
from reportlab.pdfgen import canvas
from io import BytesIO




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

            
            if user_obj.phone_number != phone_number:
                updation_validation = False
                return Response({'status' : 404,'error' : 'phone_number not match with user'})

            
            if user_obj.email != email and CustomUser.objects.filter(email = email).exists():
                updation_validation = False
                return Response({'status' : 404,'error' : 'Email already exist'})

            
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
    
class verifyOTPChangepwd(APIView):
    def post(self, request):
        try:
            phone_number = str(request.data['phone_number'])
            mobile_otp = request.data['mobile_otp']
            email_otp = request.data['email_otp']
           
            user_obj = CustomUser.objects.get(phone_number = phone_number)
            
            time_diff = (datetime.now(timezone.utc) - user_obj.otp_created_at).total_seconds()
            
            is_validate = True
            if user_obj.otp != mobile_otp or time_diff > 120:
                is_validate = False
                return Response({'status' : 403, 'message' : 'Mobile OTP not match or Expired'})
            
            time_diff = (datetime.now(timezone.utc) - user_obj.email_token_created_at).total_seconds()
            if user_obj.email_token != email_otp or time_diff > 120:
                is_validate = False
                return Response({'status' : 403, 'message' : 'Email OTP not match or Expired'})
            
            if is_validate:
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
            
            user_obj = CustomUser.objects.get(phone_number = user)
            
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



class resendEmail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = str(request.user)
            
            user_obj = CustomUser.objects.get(phone_number = user)
            
            email_token = uuid4()
            print(email_token)
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

            try:
                user_obj = CustomUser.objects.get(phone_number = user)
            except CustomUser.DoesNotExist:
                return Response({'status' : 401, 'message' : 'User not exist...'})

            if not check_password(password, user_obj.password):
                return Response({'status' : 402, 'message' : 'Mobile number and password not match'})


            is_authonthicate = True  # authentication successful
         


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
        

class StageOfCase(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Case_Stage.objects.all().order_by('stage_of_case')
    serializer_class = StageOfCaseSerializer
        



class DateUpdateCase(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request):
        try:
            print(request.data)
            user = request.user
            case_id = request.data['id']
            next_date = request.data['next_date']
            stage = request.data['stage']
            comments = request.data['comments']


            case_obj = Case_Master.objects.get(id = case_id)
            last_date_previous = case_obj.last_date
            next_date = datetime.strptime(next_date, "%Y-%m-%d").date()
           
            if next_date < last_date_previous:
               
                last_date_updated = last_date_previous
            else:
                last_date_updated = case_obj.next_date


            case_stage_obj = Case_Stage.objects.get(id = stage)
            stage_name = case_stage_obj.stage_of_case

            case_history_obj = CaseHistory.objects.create(
                case = case_obj,
                last_date = last_date_updated,
                next_date = next_date,
                particular = comments,
                stage = stage_name
            )

            case_obj.last_date = last_date_updated
            case_obj.next_date = next_date
            case_obj.stage_of_case = case_stage_obj
            case_obj.save()

            return Response({'status' : 200, 'message' : "Date Updated"})
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class CaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request):
        try:
            user = request.user
            
            #to update last login time
            user_obj = CustomUser.objects.get(phone_number = user)
            user_obj.last_login = datetime.now(timezone.utc)
            user_obj.save()
            
            case_obj = Case_Master.objects.filter(advocate = user, is_active = True).order_by('next_date')
            user_obj = CustomUser.objects.filter(phone_number = user)
            
            caseserializer = CaseSerializer(case_obj, many=True)
            userserializer = ProfileSerializer(user_obj, many=True)

            total_case = len(case_obj)
            today_cases = len(case_obj.filter(next_date = datetime.now().date())) + len(case_obj.filter(last_date = datetime.now().date()))
            tommarow_cases  = len(case_obj.filter(next_date = datetime.now().date()+timedelta(1)))
            date_awaited_case = len(case_obj.filter(next_date__lt = datetime.now().date()))

            case_obj_today = case_obj.filter(next_date = datetime.now().date())
            caseserializer = CaseSerializer(case_obj_today, many=True)
            
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



class CaseViewFiltered(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request):
        try:
            user = request.user
            case_filter = request.data['filter']
            
            case_obj = Case_Master.objects.filter(advocate = user)
        
            if case_filter == 'today':
                cases_list = case_obj.filter(
                    Q(next_date = datetime.now().date()) |
                    Q(last_date = datetime.now().date())
                    )
                
            elif case_filter == 'tommarow':
                cases_list = case_obj.filter(next_date = datetime.now().date()+timedelta(1))
            elif case_filter == 'date_awaited':
                cases_list = case_obj.filter(next_date__lt = datetime.now().date())
            else: #All cases
                cases_list = case_obj

            
            caseserializer = CaseSerializer(cases_list, many=True)
            
            
            return Response({'status' : 200, 
                             'cases' : caseserializer.data, 
                             })
        
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
    
class CaseHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            case_id = request.data['id']
            case_history_obj = CaseHistory.objects.filter(case = case_id)
            serializer = CaseHistorySerializer(case_history_obj, many=True)
            print(case_id)
            print(serializer.data)
            return Response({'status' : 200, 'payload' : serializer.data})
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class getDistrict(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    



class CaseAdd(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            cnr = request.data['cnr']
            case_no = request.data['case_no']
            year = request.data['year']
            
            state_id = request.data['state_id']
            state_name = State.objects.get(id = state_id)
            
            district_id = request.data['district_id']
            district_name = District.objects.get(id = district_id)

            court_type_id = request.data['court_type_id']
            court_type = Court_Type.objects.get(id = court_type_id)
            
            court_id = request.data['court_id']
            court_name_obj = Court.objects.get(id = court_id)
            court_name = court_name_obj.court_name
            court_no = court_name_obj.court_no
            
            case_type_id = request.data['case_type_id']
            case_type = Case_Type.objects.get(id = case_type_id)
            
            under_section = request.data['under_section'].upper()
            petitioner = request.data['petitioner'].upper()
            respondent = request.data['respondent'].upper()
            client_type = request.data['client_type']  #1 For Petitioner #2 for Respondent
            
            case_stage_id = request.data['case_stage_id']
            case_stage = Case_Stage.objects.get(id = case_stage_id)
            
            first_date = request.data['first_date']
            next_date = request.data['next_date']

            fir_no = request.data['fir_no']
            fir_year = request.data['fir_year']
            police_station = request.data['police_station']
            sub_advocate = request.data['sub_advocate']
            comments = request.data['comments']
            document = request.data['document']
            
            case_obj = Case_Master.objects.create(
                crn = cnr,
                case_no = case_no,
                case_year = year,
                state = state_name,
                district = district_name,
                court_type = court_type,
                court_name = court_name,
                court_no = court_no,
                case_type = case_type,
                under_section = under_section,
                petitioner = petitioner,
                respondent = respondent,
                client_type = client_type,
                stage_of_case = case_stage,
                fir_number = fir_no,
                fir_year = fir_year,
                police_station = police_station,

                first_date = datetime.strptime(first_date, '%Y-%m-%d').date(),

                last_date = first_date,
                next_date = datetime.strptime(next_date, '%Y-%m-%d').date(),
                advocate = user,
                sub_advocate = sub_advocate,
                comments = comments,
                document = document,
                court_id = court_name_obj,
                
            )


            #add data in case history modale
            casehistoryObj = CaseHistory.objects.create(
                case = case_obj,
                last_date = case_obj.last_date,
                next_date = case_obj.next_date,
                particular = case_obj.comments,
                stage = case_obj.stage_of_case,

            )

            if document != "":

                casedocument_obj = Case_Document.objects.create(
                    case = case_obj,
                    document = document,
                    document_name = "Case_Document",
                    document_description = "",
                    document_date = datetime.now().date(),
                    document_uploaded_by = case_obj.advocate
                )

            print(request.data)

            return Response({'status' : 200,'message' : 'Case Add Successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
    

class CaseEdit(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            case_id = request.data['id']
            
            cnr = request.data['cnr']
            case_no = request.data['case_no']
            year = request.data['year']
            state_id = request.data['state_id']
            state_name = str(State.objects.get(id = state_id))
            district_id = request.data['district_id']
            district_name = str(District.objects.get(id = district_id))
            court_type_id = request.data['court_type_id']
            court_type = str(Court_Type.objects.get(id = court_type_id))
            
            court_id = request.data['court_id']
            court_name_obj = Court.objects.get(id = court_id)
            court_name = court_name_obj.court_name
            court_no = court_name_obj.court_no
            case_type_id = request.data['case_type_id']
            case_type = Case_Type.objects.get(id = case_type_id)
            under_section = request.data['under_section']
            petitioner = request.data['petitioner'].upper()
            respondent = request.data['respondent'].upper()
            client_type = request.data['client_type']  #1 For Petitioner #2 for Respondent
            case_stage_id = request.data['case_stage_id']
            case_stage = Case_Stage.objects.get(id = case_stage_id)
            next_date = request.data['next_date']
            fir_no = request.data['fir_no']
            fir_year = request.data['fir_year']
            police_station = request.data['police_station']
            sub_advocate = request.data['sub_advocate']
            comments = request.data['comments']
            
            is_case_desided = request.data['is_desided']

            case_obj = Case_Master.objects.get(id = case_id)
            case_obj.crn = cnr
            case_obj.case_no = case_no
            case_obj.case_year = year
            case_obj.state = state_name
            case_obj.district = district_name
            case_obj.court_type = court_type
            case_obj.court_name = court_name
            case_obj.court_no = court_no
            case_obj.case_type = case_type
            case_obj.under_section = under_section
            case_obj.petitioner = petitioner
            case_obj.respondent = respondent
            case_obj.client_type = client_type
            case_obj.stage_of_case = case_stage
            case_obj.fir_number = fir_no
            case_obj.fir_year = fir_year
            case_obj.police_station = police_station
            case_obj.next_date = datetime.strptime(next_date, '%Y-%m-%d').date()
            
            print(is_case_desided)
            if is_case_desided == True:
                case_obj.last_date = case_obj.next_date
                case_obj.next_date = datetime.now().date()
                case_obj.is_desided = True
                case_obj.is_active = False

            case_obj.sub_advocate = sub_advocate
            
            case_obj.save()
            #add data in case history modale
            print("2")
            if is_case_desided == True:
                print("2.1")
                casehistoryObj = CaseHistory.objects.create(
                    case = case_obj,
                    last_date = case_obj.last_date,
                    next_date = case_obj.next_date,
                    particular = comments,
                    stage = case_obj.stage_of_case,

                )
            

            print(request.data)

            return Response({'status' : 200,'message' : 'Case Edit Successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
    
class CaseClosedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            print(request.data)
            case_id = request.data['id']
            comments = request.data['comments']

            is_case_desided = request.data['is_desided']

            case_obj = Case_Master.objects.get(id = case_id)

            print(is_case_desided)
            case_obj.last_date = case_obj.next_date
            case_obj.next_date = datetime.now().date()
            if is_case_desided == True:
                case_obj.is_desided = True
                case_obj.is_active = False
                particular = "Case Closed"
            else:
                case_obj.is_active = True
                case_obj.is_desided = False
                particular = "Case Reopen"
            
            case_obj.save()
            #add data in case history modale
            print("2")

            casehistoryObj = CaseHistory.objects.create(
                case = case_obj,
                last_date = case_obj.last_date,
                next_date = case_obj.next_date,
                particular = particular,
                stage = case_obj.stage_of_case,

            )


            print(request.data)

            return Response({'status' : 200,'message' : 'Case Edit Successfully'})

        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})




class CaseViewDetailByID(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print(request.data)
            case_obj = Case_Master.objects.get(id = request.data['id'])
            caseserializer = CaseByIDSerializer(case_obj)
            
            
            return Response({'status' : 200, 
                             'cases' : caseserializer.data, 
                             })
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        
    
class CaseViewDetailCalander(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            
            user = request.user
            print(user)
            req_month = request.data['req_month']
            req_year = request.data['req_year']
            case_obj = CaseHistory.objects.filter(
                Q(last_date__month = req_month, last_date__year = req_year, case__advocate = user) |
                Q(next_date__month = req_month, next_date__year = req_year, case__advocate = user)
                ).order_by('last_date')
            casehistoryserializer = CaseHistorySerializer(case_obj, many=True)
            print(case_obj)
            
            return Response({'status' : 200, 
                             'cases' : casehistoryserializer.data, 
                             })
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



class ForgatPassword(APIView):
    def post(self, request):
        try:
            user = request.data['phone_number']
            user_obj = CustomUser.objects.filter(phone_number = user)
            if not user_obj.exists():
                return Response({'status' : 401, 'message' : 'User not exist...'})

            user_obj = CustomUser.objects.get(phone_number = user)
            
            #generae mobile otp
            otp = generate_otp()
            user_obj.otp = otp
            otp_msg = f'Hi, {user} Welcome back. For recover your password, Your Mobile OTP is {otp}'
            send_msg_to_mobile(user, otp, otp_msg)
            user_obj.otp_created_at = datetime.now(timezone.utc)

            #generate email otp
            otp = generate_otp()
            user_obj.email_token = otp
            email_msg = f'Hi, {user} Welcome back. For recover your password, Your Email OTP is {otp}'
            user_obj.email_token_created_at = datetime.now(timezone.utc)
            send_email_otp(user_obj.email, otp, email_msg)
            user_obj.save()   

            return Response({'status' : 200, 'message' : 'Forgate Password change OTP send successfully'})
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class ChangePassword(APIView):
    def post(self, request):
        try:
            user = request.data['phone_number']
            password = request.data['password']
      

            try:
                return self._extracted_from_post_10(user, password)
            except Exception as e:
                print(e)
                return Response({'status' : 401, 'message' : 'User not exist...'})


        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'}) 

    # TODO Rename this here and in `post`
    def _extracted_from_post_10(self, user, password):
        user_obj = CustomUser.objects.get(phone_number = user)
       
        user_obj.password = make_password(password)
        user_obj.save()
       
        return Response({'status' : 200, 'message' : 'password change successfully'}) 

class getCourtType(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Court_Type.objects.all()
    serializer_class = CourtTypeSerializer

class getCaseType(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Case_Type.objects.all().order_by('case_type')
    serializer_class = CaseTypeSerializer

class CourtUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print(request.data)
            case_id = request.data['case_id']
            court_id = request.data['court_id']


            court_name_obj = Court.objects.get(id = court_id)
            court_name = court_name_obj.court_name
            court_no = court_name_obj.court_no
            
            case_obj = Case_Master.objects.get(id = case_id)
            old_court = case_obj.court_no

            case_obj.court_name = court_name
            case_obj.court_no = court_no
            case_obj.court_id = court_name_obj
            case_obj.save()

            CourtTransfer.objects.create(
                case = case_obj,
                date = datetime.now().date(),
                old_court = old_court,
                new_court = court_no,
            )

            return Response({'status' : 200, 'message' : "court updated successfully"})
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})
        
        
class getCourt(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print(request.data)
            district_id = request.data['district_id']
            print(district_id)
            court_obj = Court.objects.filter(district = district_id)
            print(court_obj)
            if not court_obj.exists():
                return Response({'status' : 404, 'message' : 'Court not exist'})
            serializer = CourtSerializer(court_obj, many=True)
            
            print(serializer.data)
            return Response({'status' : 200, 'payload' : serializer.data})
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})



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




from rest_framework.permissions import AllowAny
from django.http import FileResponse
from advocatediary.scheduler.scheduler import generate_daily_pdf
class DataPDFView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        pdf_buffer = generate_daily_pdf()
        return FileResponse(pdf_buffer, as_attachment=True, filename="data_report.pdf")




  