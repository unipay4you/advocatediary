
import datetime
from django.contrib import messages
import re, random

from django.shortcuts import render, redirect
from v1.models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model  
from v1.dj_city import *
from django.db.models import Max,Min,Q





def validate_phone_number(phone_number):
    is_phone_number_valid = False

    is_phone_number_valid = phone_number.isnumeric()
    
    try:
        if not is_phone_number_valid:
            return False, "phone number not valid"
        elif len(phone_number) != 10:
            return False, "phone number must be 10 digit"

        else:
            return True, "Valid phone number"
        
    except Exception as e:
        print(e)



def validate_password(password):
    is_password_valid = True
    try:
        while True:
            if (len(password)<=8):
                is_password_valid = False
            elif not re.search("[a-z]", password):
                is_password_valid = False
            elif not re.search("[A-Z]", password):
                is_password_valid = False
            elif not re.search("[0-9]", password):
                is_password_valid = False
            elif not re.search("[_@$]" , password):
                is_password_valid = False
            elif re.search(" " , password):
                is_password_valid = False
            else:
                is_password_valid = True
                
            break

        if is_password_valid == False:
            return False, "Password must be AlfaNumeric and 8 digit long and must contain special character and atleast one upper case and lower case"
        else:
            return True, "Valid Password"
                
    except Exception as e:
        print(e)
        return False, "Password not valid"
    

def generate_user_id():
        not_unique = True
        while not_unique:
            user_id = random.randint(100000, 999999)
            
            if not (is_user_id_exist := User_ID.objects.filter(user_id=user_id).exists()):
                not_unique = False
        return str(user_id)

def send_otp_to_mobile(phone_number, otp, msg):
    return None


    
def send_mail_token(email, email_token):
    try:
        address = [email,]
        subject = 'Your Account need to be verified'
        message = f'Click on the link to verify your email https://mylegaldiary.in/verify/{email_token}'
        obj = send_mail(subject, message, settings.EMAIL_HOST_USER, address)
        print('Mail send successfull')
    
    except Exception as e:
        print(e)    
    

def check_login_validation(phone_number):
    
    user = CustomUser.objects.get(phone_number = phone_number)
    last_login = user.last_login
    
    time_current = datetime.datetime.now(datetime.timezone.utc)

    time_diff = time_current - last_login
    time_diff = time_diff.total_seconds()

    if time_diff > 1800:
        return False
    

    update_last_login(phone_number)
    return True
    

def update_last_login(phone_number):
    user = CustomUser.objects.get(phone_number = phone_number)
    user.last_login = datetime.datetime.now(datetime.timezone.utc)
    print(user.last_login)
    user.save()

#check firsttime log in 
def is_first_time_login(phone_number):
    user = CustomUser.objects.get(phone_number = phone_number)

    if user.is_first_login:
        return True
    

def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def update_city():
    for state in cities:
        print(state[0])
        state_obj = State.objects.create(state = state[0])
        for city in state[1]:
            print(city[0])
            
            District.objects.create(district = city[0], state = state_obj)


def get_district(request):
    state_id = request.GET['state_id']
    get_state = State.objects.get(id=state_id)
    districts = District.objects.filter(state=get_state).order_by('district')
    return render(request, 'get_district.html', locals())

def add_new_district(request):
    status = False
    state_id = request.GET['state_id']
    get_state = State.objects.get(id=state_id)
    district_id = request.GET['district_id']
    district_name = request.GET['district_name']
    district_name = district_name.capitalize()
    if district_id == 'Add_new_District':
        if (is_district_exist := District.objects.filter(Q(district__icontains=district_name) & Q(state__state__icontains = get_state)).exists()):
            msg = "District already exist."
            status = False
        
        else:
            District.objects.create(district = district_name, state = get_state)
            
            msg = "DONE"
            status = True
        
    context = {
        'status' : status,
        'msg' : msg,
     }
    return render(request, 'add_new_district.html',context)
    
    
def get_court(request):
    state_id = request.GET['state_id']
    get_state = State.objects.get(id=state_id)
    district_id  = request.GET['district_id']
    district_name = District.objects.get(id=district_id)
    courts = Court.objects.filter(Q(district=district_name) & Q(state = get_state)).order_by('court_name')
    return render(request, 'get_court.html', locals())


def add_new_court(request):
    state_id = request.GET['state_id']
    state_name = State.objects.get(id=state_id)
    district_id  = request.GET['district_id']
    district_name = District.objects.get(id=district_id)
    court_id  = request.GET['court_id']
    court_type  = request.GET['court_type']
    get_court_type = Court_Type.objects.get(id=court_type)
    court_name  = request.GET['court_name']
    court_name = court_name.upper()
    court_no  = request.GET['court_no']
    court_no = court_no.upper()

    status = False
    if court_id == 'Add_new_Court':
        if (is_court_exist := Court.objects.filter(
            Q(district__district__icontains=district_name) & 
            Q(state__state__icontains = state_name) &
            Q(court_type__court_type__icontains = get_court_type) &
            Q(court_name__icontains=court_name) &
            Q(court_no__icontains=court_no)
            ).exists()):
            msg = "Court already exist."
            status = False
        
        else:
            Court.objects.create(
                district = district_name, 
                state = state_name, 
                court_name = court_name, 
                court_type = get_court_type, 
                court_no = court_no
                )
            
            msg = "DONE"
            status = True
        
    context = {
        'status' : status,
        'msg' : msg,
     }
    return render(request, 'add_new_court.html', context)


