from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from v1.models import *
from django.contrib.messages import constants as messages
from django.contrib import messages
from v1.helper import *
from django.core.exceptions import ValidationError
import datetime
import random
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email






# Create your views here.

def base(request):
    return render(request, 'base.html')

def LOGIN(request):
    if request.method != 'POST':
        return render(request, 'login.html')
    phone_number = request.POST.get('mobile')
    password = request.POST.get('password')

    user = CustomUser.objects.filter(phone_number = phone_number)
    if not user.exists():
        messages.error(request, "user not exist, plz register first......")
        return redirect('login')

    user = authenticate(phone_number = phone_number, password = password)

    if user is None:
        messages.error(request, "Mobile number and password not match")
        return redirect('login')
    else:
        #check user mobile verify or not
        login(request, user)

        request.session['phone_number'] = user.phone_number
        request.session['email'] = user.email
        

        if user.is_phone_number_verified & user.is_email_verified:
            if not user.is_first_login:
                if user.user_type == 'admin':
                    return HttpResponse('Admin page')
                elif user.user_type == 'advocate':
                    return redirect('adv_index')
                elif user.user_type == 'staff':
                    return HttpResponse('staff page')
                else:
                    return HttpResponse('invalid roll')
                    
            

            return redirect('profile')
        return redirect('otp_verify')

        
def logout_page(request):
    logout(request)
    return redirect('login')


    
def REGISTER(request):
    try:
        return _extracted_from_REGISTER_4(request)
    except Exception as e:
        print(e)
        return redirect('register')


# TODO Rename this here and in `REGISTER`
def _extracted_from_REGISTER_4(request):
    #is_valid = False means found error in validation
    if request.method != 'POST':
        context = {
            'is_otp_genrated' : False,
        }
        return render(request, 'register.html', context)

    is_valid = True
    
    phone_number = request.POST.get('mobile')
    user_name = request.POST.get('user_name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    
    #validate user name is valid or not
    is_user_name_valid = user_name != '' and all(chr.isalpha() or chr.isspace() for chr in user_name)
    if not is_user_name_valid:
        is_valid = False
        msg = "User name contain only alphabets and space"
        messages.error(request, msg)
    
    #validate phone number is valid or not
    is_valid_phone_number, msg = validate_phone_number(phone_number)
    if not  is_valid_phone_number:
        is_valid = False
        messages.error(request, msg)
    
    
    #validate password is valid or not
    if password != confirm_password:
        is_valid = False
        msg = "Password and Confirm Password does not match"
        messages.error(request, msg)
    
    is_valid_password, msg = validate_password(password)
    if not is_valid_password:
        is_valid = False    
        messages.error(request, msg)

    
    #validate email
    if (is_email_exist := CustomUser.objects.filter(email = email).exists()):
        is_valid = False
        msg = "Email already exist"
        messages.error(request, msg)
    
    if is_valid:
        #check phone number already exist or not
        if not (
            is_phone_number_exist := CustomUser.objects.filter(
                phone_number=phone_number
            ).exists()
        ):
            return _extracted_from_REGISTER(request,phone_number, user_name, password, email)
            
        is_valid = False
        msg = "Phone number already exist"
        messages.error(request, msg)

    context = {
        'phone_number': phone_number,
        'user_name': user_name,
        'password': password,
        'confirm_password': confirm_password,
        'is_otp_genrated': False,
        'email' : email,
        }
    return render(request, 'register.html', context)

# TODO Rename this here and in `REGISTER`
def _extracted_from_REGISTER(request, phone_number, user_name, password, email):
    user_type = 'advocate'
    is_phone_number_verified = False
    is_email_verified = False
    is_first_login = True
    otp = random.randint(100000, 999999)
    user_id = generate_user_id()
    otp_msg = ''
    otp_created_at = datetime.datetime.now(datetime.timezone.utc)
    otp_send_obj = send_otp_to_mobile(phone_number, otp, otp_msg)
    user_id_ref = User_ID.objects.create(user_id=user_id)

    user = CustomUser.objects.create(
        phone_number=phone_number,
        user_name=user_name,
        user_type=user_type,
        is_phone_number_verified = is_phone_number_verified,
        is_email_verified = is_email_verified,
        is_first_login = is_first_login,
        otp = otp,
        email = email,
        user_id = user_id_ref,
        otp_created_at = otp_created_at
        
        
    )

    user.set_password(password)
    user.save()

    request.session['phone_number'] = phone_number
    return redirect('otp_verify')


def RESEND_OTP(request):
    otp = random.randint(100000, 999999)
    phone_number = request.session.get('phone_number')
    otp_msg = ''
    otp_send_obj = send_otp_to_mobile(phone_number, otp, otp_msg)

    user = CustomUser.objects.get(phone_number=phone_number)
    otp_created_at = user.otp_created_at
   
    time_current = datetime.datetime.now(datetime.timezone.utc)
   
    time_diff = time_current - otp_created_at
    time_diff = time_diff.total_seconds()

   
    if time_diff > 180:
        user.otp = otp
        user.otp_created_at = time_current
        user.save()
        messages.success(request, 'OTP Send successfully')
    else:
        messages.success(request, 'Otp resend after 3 min')

    return redirect('otp_verify')




def DO_REGISTER(request):
    if request.method == 'POST':
        phone_number = request.POST.get('mobile')
        otp = request.POST.get('otp')

        user = CustomUser.objects.get(phone_number=phone_number)
        if user.otp == otp:
            user.is_phone_number_verified = True
            user.save()
            messages.success(request, 'Phone number verified successfully')
            return redirect('login')
        else:
            messages.error(request, 'OTP does not match')
            return redirect('register')


def OTP_VERIFY(request):
    if request.method != 'POST':
        return _extracted_from_OTP_VERIFY_3(request)
    otp = request.POST.get('otp')
    phone_number = request.session.get('phone_number')


    user = CustomUser.objects.get(phone_number=phone_number)

    otp_created_at = user.otp_created_at
    time_current = datetime.datetime.now(datetime.timezone.utc)

    time_diff = time_current - otp_created_at
    time_diff = time_diff.total_seconds()

    email = user.email
    email_token = uuid.uuid4()

    email_token_created_at = datetime.datetime.now(datetime.timezone.utc)
    if time_diff < 180:
        if user.otp == otp:
            return _extracted_from_OTP_VERIFY_29(
                user, email_token, email_token_created_at, request, email
            )
        else:
            messages.error(request, 'OTP does not match')
    else:
        messages.error(request, 'OTP Expired')

    return redirect('otp_verify')


# TODO Rename this here and in `OTP_VERIFY`
def _extracted_from_OTP_VERIFY_3(request):
    phone_number = request.session.get('phone_number')
    email = request.session.get('email')
    user = CustomUser.objects.get(phone_number=phone_number)
    is_phone_number_verified = user.is_phone_number_verified
    is_email_verified = user.is_email_verified
    
    if not phone_number:
        return redirect('register')
    context = {
        'phone_number' : phone_number,
        'email' : email,
        'is_phone_number_verified' : is_phone_number_verified,
        'is_email_verified' : is_email_verified
    }
    return render(request, 'otp_verify.html', context)


# TODO Rename this here and in `OTP_VERIFY`
def _extracted_from_OTP_VERIFY_29(user, email_token, email_token_created_at, request, email):
    user.is_phone_number_verified = True
    user.email_token = email_token
    user.email_token_created_at = email_token_created_at
    send_mail_token(email, email_token)
    user.save()
    messages.success(request, 'Phone number verified successfully and Verification email send on mail id')
    return redirect('login')

def VERIFY(request, email_token):
    try:
        user = CustomUser.objects.get(email_token = email_token)
        email_token_created_at = user.email_token_created_at

        time_current = datetime.datetime.now(datetime.timezone.utc)

        time_diff = time_current - email_token_created_at
        time_diff = time_diff.total_seconds()

        if time_diff > 14400:
            return HttpResponse('Link Expired, Kindly login for regenerate link')
        user.is_email_verified = True
        user.save()
        return HttpResponse('Email Verified, you can now login in your account')



    except Exception as e:
        return HttpResponse('Invalid request')


def resend_email_link(request):
    phone_number = request.session.get('phone_number')

    user = CustomUser.objects.get(phone_number=phone_number)

    email_token_created_at = datetime.datetime.now(datetime.timezone.utc)

    email = user.email
    email_token = uuid.uuid4()
    user.email_token = email_token
    user.email_token_created_at = email_token_created_at
    send_mail_token(email, email_token)
    user.save()
    messages.success(request, 'Verification email has been send on mail id')
    return redirect('otp_verify')

@login_required(login_url = 'login')
def PROFILE(request):
    phonen_number = request.session.get('phone_number')
    return render(request, 'profile.html')


@login_required(login_url = 'login')
def PROFILE_EDIT(request):  # sourcery skip: low-code-quality
    is_form_data_validate = True
    phone_number = request.session.get('phone_number')
    session_email = request.session.get('email')
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    states = State.objects.all()

    if request.method == 'POST':
        user = CustomUser.objects.get(phone_number = phone_number)

        user_name = request.POST.get('user_name')
        user_name = user_name.capitalize()
        user.user_name = user_name

        dob = request.POST.get('dob')
        user.user_dob = dob

        email = request.POST.get('email')
        is_email_valid = validateEmail(email)
        if not is_email_valid:
            is_form_data_validate = False
            messages.error(request, 'Invalid Email')

# sourcery skip: merge-nested-ifs
        if CustomUser.objects.filter(email = email).exists():
            if session_email != email:
                is_form_data_validate = False
                messages.error(request, 'Email already exist')


        if session_email != email:
            user.is_email_verified = False
        user.email = email

        advocate_registration_number = request.POST.get('advocate_registration_number')
        advocate_registration_number = advocate_registration_number.capitalize()
        user.advocate_registration_number = advocate_registration_number

        address1 = request.POST.get('address1')
        address1 = address1.capitalize()
        user.user_address1 = address1

        address2 = request.POST.get('address2')
        address2 = address2.capitalize()
        user.user_address2 = address2

        address3 = request.POST.get('address3')
        address3 = address3.capitalize()
        user.user_address3 = address3

        state_id = request.POST.get('state')
        if state_id == '0' or state_id is None:
            is_form_data_validate = False
            messages.error(request, 'Invalid State')
        getState = State.objects.get(id = state_id)
        user.user_state = getState


        district_id = request.POST.get('district')
        if district_id == 0 or district_id is None:
            is_form_data_validate = False
            messages.error(request, 'Invalid District')
        getDistrict = District.objects.get(id = district_id)
        user.user_district = getDistrict

        pincode = request.POST.get('pincode')
        is_pincode_valid = pincode.isnumeric()
        if not is_pincode_valid or len(pincode) != 6:
            is_form_data_validate = False
            messages.error(request, 'Pincode Should be numeric and six digit')
        user.user_district_pincode = pincode

        profile_pic = request.FILES.get('profile_pic')
        if profile_pic not in [None, '']:
            user.user_profile_image = profile_pic

        if not is_form_data_validate:
            user = {
                'user_name' : user_name,
                'user_dob' : dob,
                'phone_number' : phone_number,
                'email' : email,
                'advocate_registration_number' : advocate_registration_number,
                'address1' : address1,
                'address2' : address2,
                'address3' : address3,
                'state_id' : state_id,
                'district_id' : district_id,
                'user_distric_pincode' : pincode,


            }

            context = {
            'states' : states,
            'user' : user,

            }
            return render(request, 'profile_edit.html', context)
        user.is_first_login = False
        user.save()
        return redirect('profile') if is_email_valid else redirect('login')
    user = CustomUser.objects.get(phone_number = phone_number)


    context = {
        'states' : states,
        'user' : user,

    }
    return render(request, 'profile_edit.html', context)

@login_required(login_url = 'login')
def DELINK_CASE(request, id):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)
    
    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')

    associate_case_id = id
    associate_case_obj = Associate_With_Client.objects.get(id = associate_case_id)
    associate_case_obj.is_deleted=True
    associate_case_obj.save()
    
    return redirect('allclients')

@login_required(login_url = 'login')
def DELETE_CLIENT(request, id):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)
    
    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')

    client_id = id
    print(client_id)
    client_obj = Clients.objects.get(id = client_id)
    client_obj.is_deleted=True
    client_obj.save()

    associate_case_obj = Associate_With_Client.objects.filter(id = client_obj)
    for associate_case in associate_case_obj:
        associate_case.is_deleted=True
        associate_case.save()
    

    
    return redirect('allclients')   
    

    