from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from v1.helper import *


@login_required(login_url = 'login')
def adv_index(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    is_first_login = is_first_time_login(phone_number)

    if is_first_login:
        return redirect('profile')

    return render(request, 'advocate/adv-index.html')


@login_required(login_url = 'login')
def NEWCASE(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')

    end_year = datetime.datetime.now().year
    year_rage = range(1970, end_year + 1)

    states = State.objects.all()
    court_type = Court_Type.objects.all()
    case_type = Case_Type.objects.all()
    case_stage = Case_Stage.objects.all()

    context = {
            'year_rage' : year_rage,
            'states' : states,
            'court_type' : court_type,
            'case_type' : case_type,
            'case_stage' : case_stage
            }
    
    return render(request, 'advocate/newcase.html', context)



    

