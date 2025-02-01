from faker import Faker
import random
from v1.models import *
from v1.helper import *
from django.db.models import Q, Sum
from datetime import datetime, timedelta

fake = Faker()

def create_fake_users(n):

    user_type = 'advocate'
    user_address1 = 'test'
    user_address2 = 'address 2'
    user_address3 = 'address 3'
    user_state = 'Rajasthan'
    user_district = 'Kota'
    user_district_pincode = '324004'

    user_under_which_advocate = ''
    is_phone_number_verified = True
    is_email_verified = True
    is_first_login = False
    password = 'Dharm@123'
    for _ in range(n):
        user_id = generate_user_id()
        user_id_ref = User_ID.objects.create(user_id=user_id)
        user_id = user_id_ref
        user_name = fake.name()
        user_dob = fake.date_of_birth()
        state_obj = State.objects.get(state = user_state)
        district_obj = District.objects.get(district = user_district)
        ran_number = random.randint(1,5000)
        ran_year = random.randint(1990, 2024)
        advocate_registration_number =f"R/{ran_number}/{ran_year}"
        last_login = datetime.datetime.now(datetime.timezone.utc)
        phone_number = generate_random_phone_number()

        user = CustomUser.objects.create(
            phone_number=phone_number,
            user_name=user_name,
            user_type=user_type,
            is_phone_number_verified = is_phone_number_verified,
            is_email_verified = is_email_verified,
            is_first_login = is_first_login,
            user_id = user_id_ref,
            user_dob = user_dob,
            user_address1 =user_address1,
            user_address2 =user_address2,
            user_address3 =user_address3,
            user_state = state_obj,
            user_district =district_obj,
            user_district_pincode =user_district_pincode,
            advocate_registration_number = advocate_registration_number,
            last_login = last_login,
        )

        user.set_password(password)
        user.save()

def generate_random_phone_number():
        not_unique = True
        while not_unique:
            phone_number = random.randint(900000001, 999999999)
            
            if not (is_user_id_exist := CustomUser.objects.filter(phone_number=phone_number).exists()):
                not_unique = False
        return str(phone_number)

def create_fake_client(n):
    for _ in range(n):
        name = fake.name()
        address = fake.address()
        mobile = generate_random_phone_number()
        advocate_obj = CustomUser.objects.all()
        rand_index = random.randint(0, len(advocate_obj) - 1)
        print(rand_index)
        advocate = advocate_obj[rand_index]
        Clients.objects.create(
             name = name,
             address = address,
             mobile = mobile,
             advocate = advocate
        )


def create_fake_cases(n):
    state_name = 'Rajasthan'
    district_name = 'Kota'
    fir_no = ''
    fir_year = ''
    police_station = ''
    sub_advocate = ''
    comments = ''
    document = ''

    for _ in range(n):
        cnr = random.randint(1111111111,9999999999)
        case_no = random.randint(1, 99999)
        year = random.randint(1990,2025)
        print('court_name')
        court_id_obj = Court.objects.all()
        rand_court_id = random.randint(1, len(court_id_obj) - 1)
        print(rand_court_id)
        court_name_obj = Court.objects.get(id = rand_court_id)
        court_name = court_name_obj.court_name
        print(court_name)

        court_no = court_name_obj.court_no

        print('case_type')
        case_type_obj = Case_Type.objects.all()
        case_type_id = random.randint(1, len(case_type_obj) - 1)
        print(case_type_id)
        case_type = Case_Type.objects.get(id = case_type_id)
        print(case_type)

        under_section = random.randint(0, 99)

        petitioner = fake.name()
        respondent = fake.name()

        rand_id = random.randint(1,2)
        client_type = 'Petitioner' if rand_id == 1 else 'Respondent'
        
        print('case_stage')
        case_stage_obj = Case_Stage.objects.all()
        case_stage_id = random.randint(1, len(case_stage_obj) - 1)
        print(case_stage_id)
        case_stage = Case_Stage.objects.get(id = case_stage_id)
        print(case_stage)

        first_date = fake.date_between(start_date="-10y")
        next_date = fake.date_between(start_date="-1w", end_date="+1y")

        print('user')
        advocate_obj = CustomUser.objects.all()
        advocate_rand_id = random.randint(1, len(advocate_obj) - 1)
        print(advocate_rand_id)
        user = CustomUser.objects.get(id = advocate_rand_id)
        print(user)

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

            first_date = first_date,

            last_date = first_date,
            next_date = next_date,
            advocate = user,
            sub_advocate = sub_advocate,
            comments = comments,
            document = document
        )


def rand_associate_clients():  # sourcery skip: avoid-builtin-shadow
    case_obj = Case_Master.objects.all()

    for case in case_obj:
        rand_range = range(random.randint(0,4))
        print(rand_range)
        for _ in rand_range:
            print(case.advocate)
            client_obj = Clients.objects.filter(advocate = case.advocate)
            rand_client_id = random.randint(1, len(client_obj))
            print(rand_client_id)
            client = Clients.objects.get(id = rand_client_id)
            print(client)

            client_associate = Associate_With_Client.objects.create(
                client = client,
                case = case
            )
        
        


