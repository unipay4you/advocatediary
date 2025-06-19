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
from actbook.models import *



@login_required(login_url = 'login')
def adv_index(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    user_obj = CustomUser.objects.get(phone_number = phone_number)
    if not user_obj.is_superuser:
        is_superuser = False
    else:
        is_superuser = True

    all_case = Case_Master.objects.filter(advocate = phone_number, is_active = True).order_by('next_date')
    
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
        'case_stage_obj' : case_stage_obj,
        'is_superuser' : is_superuser,
        
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
    case_type = Case_Type.objects.all().order_by('case_type')
    case_stage = Case_Stage.objects.all().order_by('stage_of_case')

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
        particular = case_obj.comments,
        stage = case_obj.stage_of_case,

    )

    request.session['case_obj'] = case_obj.id
    targetURL = f'/advocate/case_client_associate/{case_obj.id}'
    return redirect(targetURL)


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
def Case_Client_Associate(request, id):
    phone_number = request.user
    case_obj = id
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    #get Advocate id from user login
    user = CustomUser.objects.get(phone_number = phone_number)
    get_case = '0'
    
    Associate_With_Client_obj = ''
    if case_obj != '0':
        get_case = Case_Master.objects.get(id = case_obj)
        Associate_With_Client_obj = Associate_With_Client.objects.filter(case = case_obj)
    else:
        get_case = Case_Master.objects.filter(advocate = user)
    
    client_all = Clients.objects.filter(advocate = user).order_by('name')
    
    
    
    
    context = {
        'case' : get_case,
        'clients' : client_all,
        'associate_with_client' : Associate_With_Client_obj,
        'case_obj' : case_obj
    }
    return render(request, 'advocate/case_client_associate.html', context)    

@login_required(login_url = 'login')
def associate_client_and_add_more(request):
    phone_number = request.user
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

@transaction.atomic
@login_required(login_url = 'login')
def CASEEDIT(request, id):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    case_obj = Case_Master.objects.get(id = id)
    court_obj = Court.objects.filter(state__state__contains = case_obj.state, district__district__contains = case_obj.district).order_by('court_no')
    case_type_obj = Case_Type.objects.all()
    case_stage = Case_Stage.objects.all()

    if request.method == 'POST':
        return _extracted_from_CASEEDIT(request, case_obj)

    context = {
        'case_obj' : case_obj,
        'court_obj' : court_obj,
        'case_type_obj' : case_type_obj,
        'case_stage' : case_stage
    }
    return render(request, 'advocate/case_edit.html', context)

def _extracted_from_CASEEDIT(request, case_obj):
    cnr = request.POST.get('cnr')
    case_no = request.POST.get('case_no')
    year = request.POST.get('year')
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
    
    fir_no = request.POST.get('fir_no')
    fir_year = request.POST.get('fir_year')
    police_station = request.POST.get('police_station')
    sub_advocate = request.POST.get('sub_advocate')
    comments = request.POST.get('comments')
    document = request.FILES.get('document')


    case_obj.crn =case_no
    case_obj.case_year = year
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

    case_obj.sub_advocate = sub_advocate
    case_obj.comments = comments
    case_obj.document = document

    case_obj.save()
    return redirect('adv_index')



@transaction.atomic
@login_required(login_url = 'login')
def act_add_view(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    if request.method == 'POST':
        return _extracted_from_NEWACT(request)

    return render(request, 'advocate/addact.html')

def _extracted_from_NEWACT(request):
    act_name_en = request.POST.get('act_name_en')
    act_image_en = request.FILES.get('act_image_en')
    act_name_hi = request.POST.get('act_name_hi')
    act_image_hi = request.FILES.get('act_image_hi')
    act_discription = request.POST.get('act_discription')
    act_short_name = request.POST.get('act_short_name')
    document_en = request.FILES.get('document_en')
    document_hi = request.FILES.get('document_hi')
    date_introduce = request.POST.get('date_introduce')
    if not date_introduce:
        date_introduce = datetime.now().date()
    else:
        date_introduce = datetime.strptime(date_introduce, '%Y-%m-%d').date()


    # Validate the inputs
    if not act_name_en or len(act_name_en) < 3:
        messages.error(request, 'Act name in English is required and must be at least 3 characters long.')
        return redirect('newact')
    
    if not act_short_name or len(act_short_name) < 3:
        messages.error(request, 'Act short name is required and must be at least 3 characters long.')
        return redirect('newact')
    if actbook.objects.filter(act_name=act_name_en).exists():
        messages.error(request, 'An act with this name already exists.')
        return redirect('newact')
    if actbook.objects.filter(act_short_name=act_short_name).exists():
        messages.error(request, 'An act with this short name already exists.')
        return redirect('newact')
    

    if act_obj := actbook.objects.create(
        act_name=act_name_en,
        act_name_hindi=act_name_hi,
        act_description=act_discription,
        act_short_name=act_short_name,
        act_date_enacted=date_introduce,
        act_pdf=document_en,
        act_pdf_hindi=document_hi,
        act_image=act_image_en,
        act_image_hindi=act_image_hi,
    ):
        messages.success(request, 'Act added successfully')
    else:
        messages.error(request, 'Failed to add act. Please try again.')
    # Optionally, you can redirect to a different page or render a success message

    return redirect('newact')  # Redirect to the new act page or any other page as needed


@transaction.atomic
@login_required(login_url = 'login')
def act_add_chapter(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    act_obj = actbook.objects.all().order_by('act_name')
    chapter_count = 0
    actId = request.GET.get('actId')
    
    if actId:
        act_obj_1 = actbook.objects.get(id=actId)
        chapter_count = actbookchapter.objects.filter(act=act_obj_1).aggregate(Max('chapter_number'))['chapter_number__max']
    
    if chapter_count is None:
        chapter_count = 0
    
    if request.method == 'POST':
        return _extracted_from_NEWCHAPTER(request)
    
    context = {
        'acts' : act_obj,
        'chapter_count' : chapter_count + 1,
        'actId' : actId
    }

    return render(request, 'advocate/addchapter.html', context)

def _extracted_from_NEWCHAPTER(request):
    actId = request.POST.get('act_id')
    act_obj = actbook.objects.get(id=actId)
    chapter_number = request.POST.get('chapter_number')
    chapter_title = request.POST.get('chapter_title_en')
    chapter_title_hindi = request.POST.get('chapter_title_hi')
    chapter_description = request.POST.get('chapter_discription')
    

    # Validate the inputs
    if not chapter_number or not chapter_title:
        messages.error(request, 'Chapter number and title are required.')
        return redirect('newchapter')
    if not chapter_title_hindi:
        messages.error(request, 'Chapter title in Hindi is required.')
        return redirect('newchapter')
    if actbookchapter.objects.filter(act=act_obj, chapter_number=chapter_number).exists():
        messages.error(request, 'An act chapter with this number already exists.')
        return redirect('newchapter')
    
    
    
    if chapter_obj := actbookchapter.objects.create(
        act=act_obj,
        chapter_number=chapter_number,
        chapter_title=chapter_title,
        chapter_title_hindi=chapter_title_hindi,
        chapter_description=chapter_description
    ):
        messages.success(request, 'Act chapter added successfully')
        
    else:
        messages.error(request, 'Failed to add act chapter. Please try again.')
        
    # Optionally, you can redirect to a different page or render a success message

    return redirect('newchapter')  # Redirect to the new act page or any other page as needed


@transaction.atomic
@login_required(login_url = 'login')
def act_add_section(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    act_obj = actbook.objects.all().order_by('act_name')
    chapter_count = []
    actId = request.GET.get('actId')
    
    if actId:
        act_obj_1 = actbook.objects.get(id=actId)
        chapter_count = actbookchapter.objects.filter(act=act_obj_1)

        section_obj = actbooksection.objects.filter(chapter__act=act_obj_1).order_by('-id').first()
        section = section_obj.section_number if section_obj else None
    
    
    if request.method == 'POST':
        from django.db import transaction, IntegrityError
        for i in range(1, 11):
            _extracted_from_NEWSECTION(request, i)
        
        return redirect('newsection')  # Redirect to the new act page or any other page as needed
    
    context = {
        'acts' : act_obj,
        'chapter_count' : chapter_count,
        'actId' : actId,
        'section' : section if 'section' in locals() else None,
    }

    return render(request, 'advocate/addsection.html', context)

def _extracted_from_NEWSECTION(request, i):
    from django.db import transaction, IntegrityError
    actId = request.POST.get('act_id')
    act_obj = actbook.objects.get(id=actId)
    chapter_id = request.POST.get('chapter_number')
    
    chapter_obj = actbookchapter.objects.get(id=chapter_id)
    section_number = request.POST.get('section_number')

    sub_section_num = request.POST.get(f'Sub_section_number_{i}')
    section_title = request.POST.get(f'section_title_en_{i}')
    section_title_hindi = request.POST.get(f'section_title_hi_{i}')
    section_text = request.POST.get(f'section_text_en_{i}')
    section_text_hindi = request.POST.get(f'section_text_hi_{i}')
    print(i)
    print(f"Sub Section Number: {sub_section_num}")
    if sub_section_num != '0':
        section_number = f"{section_number}({sub_section_num})"
    
    is_validate = True
    # Validate the inputs
    if not section_number:
        messages.error(request, 'Section number are required.')
        is_validate = False
        
    
    if actbooksection.objects.filter(chapter=chapter_obj, section_number= section_number).exists():
        messages.error(request, 'An act sub section {sub_section_num} with this number already exists in this chapter.')
        is_validate = False
    
    if sub_section_num == '':
        is_validate = False
    
        
    try:
        with transaction.atomic():
            print(is_validate)
            print(f"Sub Section Number: {section_number}")
            if is_validate and (sub_section_num != '' or sub_section_num is not None):
                
                if section_obj := actbooksection.objects.create(
                    chapter=chapter_obj,
                    section_number=section_number,
                    section_title=section_title,
                    section_title_hindi=section_title_hindi,
                    section_text=section_text,
                    section_text_hindi=section_text_hindi
                ):
                    messages.success(request, f'Act section {section_number} added successfully')
                else:
                    messages.error(request, f'Failed to add act section {section_number}. Please try again.')
    except IntegrityError  as e:
        messages.error(request, f'Error occurred while adding section {section_number}: {str(e)}')
        is_validate = False




@transaction.atomic
@login_required(login_url = 'login')
def act_add_section_bulk(request):
    phone_number = request.user
    is_login_valid = check_login_validation(phone_number)

    if not is_login_valid:
        return redirect('login')


    if is_first_login := is_first_time_login(phone_number):
        return redirect('profile')
    
    act_obj = actbook.objects.all().order_by('act_name')
    chapter_count = []
    actId = request.GET.get('actId')
    
    if actId:
        act_obj_1 = actbook.objects.get(id=actId)
        chapter_count = actbookchapter.objects.filter(act=act_obj_1)

        section_obj = actbooksection.objects.filter(chapter__act=act_obj_1).order_by('-id').first()
        section = section_obj.section_number if section_obj else None
    
    
    if request.method == 'POST':
        from django.db import transaction, IntegrityError
        for i in range(1, 21):
            _extracted_from_NEWSECTION_bulk(request, i)
        
        return redirect('newbulksection')  # Redirect to the new act page or any other page as needed
    
    context = {
        'acts' : act_obj,
        'chapter_count' : chapter_count,
        'actId' : actId,
        'section' : section if 'section' in locals() else None,
    }

    return render(request, 'advocate/bulkaddsection.html', context)

def _extracted_from_NEWSECTION_bulk(request, i):
    from django.db import transaction, IntegrityError
    actId = request.POST.get('act_id')
    act_obj = actbook.objects.get(id=actId)
    chapter_id = request.POST.get('chapter_number')
    
    chapter_obj = actbookchapter.objects.get(id=chapter_id)
    section_number = request.POST.get(f'Sub_section_number_{i}')

    print(i)
    print(f"Section Number: {section_number}")
    
    is_validate = True
    # Validate the inputs
    
    if actbooksection.objects.filter(chapter=chapter_obj, section_number= section_number).exists():
        messages.error(request, 'An act section {section_number} with this number already exists in this chapter.')
        is_validate = False
    
    if section_number == '':
        is_validate = False
    
        
    try:
        with transaction.atomic():
            print(is_validate)
            print(f"Sub Section Number: {section_number}")
            if is_validate and (section_number != '' or section_number is not None):
                
                if section_obj := actbooksection.objects.create(
                    chapter=chapter_obj,
                    section_number=section_number,
                    
                ):
                    messages.success(request, f'Act section {section_number} added successfully')
                else:
                    messages.error(request, f'Failed to add act section {section_number}. Please try again.')
    except IntegrityError  as e:
        messages.error(request, f'Error occurred while adding section {section_number}: {str(e)}')
        is_validate = False
