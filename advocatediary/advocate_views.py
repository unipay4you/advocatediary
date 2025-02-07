from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from v1.helper import *
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Max,Min,Q, Count
from datetime import datetime, timedelta
from django.db import transaction




@login_required(login_url = 'login')
def adv_index(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    all_case = Case_Master.objects.filter(advocate = phone_number).order_by('court_no')
    
    list_filter = 'today' #defalt for display today list
    if request.GET.get('filter'):
        list_filter = request.GET.get('filter')

    if list_filter == 'today':
        cases_list = all_case.filter(next_date = datetime.now().date())
    elif list_filter == 'tommarow':
        cases_list = all_case.filter(next_date = datetime.now().date()+timedelta(1))
    elif list_filter == 'date_awaited':
        cases_list = all_case.filter(next_date__lt = datetime.now().date())
    else: #All cases
        cases_list = all_case

    total_case = all_case.count
    active_case = len(all_case.filter(is_active = True))
    today_cases = len(all_case.filter(next_date = datetime.now().date()))
    tommarow_cases  = len(all_case.filter(next_date = datetime.now().date()+timedelta(1)))
    date_awaited_case = len(all_case.filter(next_date__lt = datetime.now().date()))
    

    #if request.GET.get('search'):
    #    search = request.GET.get('search')
    #    all_case = all_case.filter(
    #        Q(address__icontains = search) |
    #        Q(name__icontains = search) |
    #        Q(mobile__icontains = search)
    #        )


    paginator = Paginator(cases_list, 10)
    
    page_number = request.GET.get('page') or 1
        
    serviceDatafinal = paginator.get_page(page_number)
    totalpage = serviceDatafinal.paginator.num_pages
    page_range = paginator.get_elided_page_range(page_number, on_each_side=2, on_ends=1)
    
    current_page_number = int(page_number)
    
    case_stage_obj = Case_Stage.objects.all()
    context = {
        'total_case' : total_case,
        'active_case' : active_case,
        'today_cases' : today_cases,
        'tommarow_cases' : tommarow_cases,
        'date_awaited_case' : date_awaited_case,
        'all_case' : serviceDatafinal,
        'lastpage' : totalpage,
        'page_range' : page_range,
        'current_page_number' : current_page_number,
        'list_filter' : list_filter,
        'case_stage_obj' : case_stage_obj
        
    }

    return render(request, 'advocate/adv-index.html', context)

@transaction.atomic
@login_required(login_url = 'login')
def NEWCASE(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    first_date = request.POST.get('first_date')
    next_date = request.POST.get('next_date')
    is_valid_data = True
    if (next_date or first_date) and next_date < first_date:
        messages.error(request, 'Next Date should be same or grater from First date')
        is_valid_data = False        

    end_year = datetime.now().year
    year_rage = range(1970, end_year + 1)

    states = State.objects.all()
    court_type = Court_Type.objects.all()
    case_type = Case_Type.objects.all()
    case_stage = Case_Stage.objects.all()

    user = CustomUser.objects.get(phone_number = phone_number)

    if is_valid_data and request.method == 'POST':
        return _extracted_from_NEWCASE(request, user)

    context = {
            'year_rage' : year_rage,
            'states' : states,
            'court_type' : court_type,
            'case_type' : case_type,
            'case_stage' : case_stage,
            }
    
    return render(request, 'advocate/newcase.html', context)

def _extracted_from_NEWCASE(request, user):
    cnr = request.POST.get('cnr')
    case_no = request.POST.get('case_no')
    year = request.POST.get('year')
    state_id = request.POST.get('state')
    state_name = State.objects.get(id = state_id)
    district_id = request.POST.get('district')
    district_name = District.objects.get(id = district_id)
    court_id = request.POST.get('court')
    court_name_obj = Court.objects.get(id = court_id)
    court_name = court_name_obj.court_name
    court_no = court_name_obj.court_no
    case_type_id = request.POST.get('case_type')
    case_type = Case_Type.objects.get(id = case_type_id)
    under_section = request.POST.get('under_section').upper()
    petitioner = request.POST.get('petitioner').upper()
    respondent = request.POST.get('respondent').upper()
    client_type = request.POST.get('client_type')  #1 For Petitioner #2 for Respondent
    case_stage_id = request.POST.get('case_stage')
    case_stage = Case_Stage.objects.get(id = case_stage_id)
    first_date = request.POST.get('first_date')
    next_date = request.POST.get('next_date')

    fir_no = request.POST.get('fir_no')
    fir_year = request.POST.get('fir_year')
    police_station = request.POST.get('police_station')
    sub_advocate = request.POST.get('sub_advocate')
    comments = request.POST.get('comments')
    document = request.FILES.get('document')


    case_obj = Case_Master.objects.create(
        crn = cnr,
        case_no = case_no,
        case_year = year,
        state = state_name,
        district = district_name,
        court_type = 'District Court',
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
        document = document
    )

    #add data in case history modale

    casehistoryObj = CaseHistory.objects.create(
        case = case_obj,
        last_date = case_obj.last_date,
        next_date = case_obj.next_date,
        particular = case_obj.comments
    )

    request.session['case_obj'] = case_obj.id
    return redirect('case_client_associate')


@login_required(login_url = 'login')
def ALLCLIENTS(request):  # sourcery skip: avoid-builtin-shadow
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    #get Advocate id from user login
    user = CustomUser.objects.get(phone_number = phone_number)
    if request.method == 'POST':
        client_Name = request.POST.get('client_Name').upper()
        mobile = request.POST.get('mobile')

        if mobile:
            is_phone_number_valid, msg = validate_phone_number(mobile)

            if not is_phone_number_valid:
                messages.error(request, 'Phone number not valid')

        address = request.POST.get('address')

        Clients.objects.create(
            name = client_Name,
            address = address,
            mobile = mobile,
            advocate = user
        )
        return redirect('allclients')
        
    allclients = Clients.objects.filter(advocate = user).order_by('name')
    
    
    if request.GET.get('search'):
        search = request.GET.get('search')
        allclients = allclients.filter(
            Q(address__icontains = search) |
            Q(name__icontains = search) |
            Q(mobile__icontains = search)
            )

    count_obj = Associate_With_Client.objects.values('client').annotate(count = Count('client'))
    for client in allclients:
        for client_obj in count_obj:
            if client.id == client_obj['client']:
                client.count = client_obj['count']
                break
            else:
                client.count = 0
                
    paginator = Paginator(allclients, 10)
    
    page_number = request.GET.get('page') or 1
        
    serviceDatafinal = paginator.get_page(page_number)
    totalpage = serviceDatafinal.paginator.num_pages
    page_range = paginator.get_elided_page_range(page_number, on_each_side=2, on_ends=1)
    
    current_page_number = int(page_number)
    
    
    
    
        
    context = {
        'allclients' : serviceDatafinal,
        'lastpage' : totalpage,
        'page_range' : page_range,
        'current_page_number' : current_page_number,
        
    }
    return render(request, 'advocate/allclients.html', context)

@login_required(login_url = 'login')
def Case_Client_Associate(request):
    phone_number = request.user
    case_obj = request.session.get('case_obj')
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    #get Advocate id from user login
    user = CustomUser.objects.get(phone_number = phone_number)
    get_case = Case_Master.objects.get(id = case_obj)
    client_all = Clients.objects.filter(advocate = user).order_by('name')
    Associate_With_Client_obj = Associate_With_Client.objects.filter(case = case_obj)

    
    
    context = {
        'case' : get_case,
        'clients' : client_all,
        'associate_with_client' : Associate_With_Client_obj
    }
    return render(request, 'advocate/case_client_associate.html', context)    

@login_required(login_url = 'login')
def associate_client_and_add_more(request):
    phone_number = request.user
    case_obj = request.session.get('case_obj')
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')

    client_id = request.GET.get('client_id')
    case_id = request.GET.get('case_id')

    client_obj = Clients.objects.get(id = client_id)
    case_obj = Case_Master.objects.get(id = case_id)

    if is_duplicate := Associate_With_Client.objects.filter(
        Q(client=client_obj) & Q(case=case_obj)
    ).exists():
        msg = 'Case Already associate with this client'
    else:
        associate_client_obj = Associate_With_Client.objects.create(
            client = client_obj,
            case = case_obj
        )
        msg = 'Success'

    return HttpResponse(msg)  


def Offcanvas_Body(request):
    case_id = request.GET['case_id']
    list_filter = request.GET['filter']
    case = Case_Master.objects.get(id=case_id)
    associate_clients = Associate_With_Client.objects.filter(case = case)
    request.session['case_obj'] = case_id
    return render(request, 'advocate/offcanvas_body.html', locals())


def Client_Case_view_Modal(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return HttpResponse(is_login_valid)


    if is_first_login := is_first_time_login(phone_number):
        return HttpResponse(is_login_valid)
    
    client_id = request.GET['client_id']
    all_case = Associate_With_Client.objects.filter(client = client_id)
    
    context = {
        'all_case' : all_case
    }
    return render(request,'advocate/client_case_viewmodal.html', context)