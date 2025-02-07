from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
import uuid
from django.utils.text import slugify
import random

# Create your models here.




class Advocate_UserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    #This Model is used for add common fields in all models
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = Advocate_UserManager()
    objects_admin = models.Manager()
    class Meta:
        abstract = True



class User_ID(BaseModel):
    user_id = models.CharField(max_length=10, 
                               unique=True,
                               )
    def __str__(self) -> str:
        return self.user_id

class State(models.Model):
    state = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.state

class District(models.Model):
    district = models.CharField(max_length=100,null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.district

class Bar(models.Model):
    bar = models.CharField(max_length=100,null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.district



class CustomUser(AbstractUser):
    username = None
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    phone_number = models.CharField(max_length=15, unique=True)
    profile_bio = models.TextField(max_length=500, blank=True, null=True)
    user_profile_image = models.ImageField(upload_to='media/profile_image', blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    USERNAME_FIELD = 'phone_number'
    user_type_choices = (
        ('admin', 'admin'),
        ('advocate', 'advocate'),
        ('staff', 'staff'),
    )
    user_id = models.OneToOneField(User_ID, on_delete=models.CASCADE, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=user_type_choices, default='admin')
    user_name = models.CharField(max_length=100, blank=True, null=True)
    user_dob = models.DateField(blank=True,null=True)
    user_address1 = models.CharField(max_length=100, blank=True, null=True)
    user_address2 = models.CharField(max_length=100, blank=True, null=True)
    user_address3 = models.CharField(max_length=100, blank=True, null=True)
    
    user_state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null= True)
    user_district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null= True)
    user_district_pincode = models.IntegerField(blank=True, null=True)
    advocate_registration_number = models.CharField(max_length=100, blank=True, null=True)
    user_under_which_advocate = models.CharField(max_length=100, blank=True, null=True)
    is_phone_number_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    email_token = models.CharField(max_length=200)
    email_token_created_at = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    REQUIRED_FIELDS = []
    objects = UserManager()

        

class user_login_details(BaseModel):
    user_id = models.OneToOneField(User_ID, on_delete=models.CASCADE, related_name='user_login_details')
    login_ip = models.GenericIPAddressField()
    login_device = models.CharField(max_length=100)
    login_location = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(auto_now=True)
    


class Case_Stage(models.Model):
    stage_of_case = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.stage_of_case

class Case_Type(models.Model):
    case_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.case_type

class Court_Type(models.Model):
    court_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.court_type

class Court(models.Model):
    court_name = models.CharField(max_length=50, blank=True, null=True)
    court_no = models.CharField(max_length=50, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING)
    court_type = models.ForeignKey(Court_Type, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.court_no


class Case_Master(BaseModel):
    crn = models.CharField(max_length=50, blank=True, null=True)
    case_no = models.CharField(max_length=50, blank=True, null=True)
    case_year = models.CharField(max_length=4, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    court_type = models.CharField(max_length=50, blank=True, null=True)
    court_name = models.CharField(max_length=50, blank=True, null=True)
    court_no = models.CharField(max_length=50, blank=True, null=True)
    case_type = models.ForeignKey(Case_Type,on_delete=models.DO_NOTHING, blank=True, null=True)
    under_section = models.CharField(max_length=50, blank=True, null=True)
    petitioner = models.CharField(max_length=50, blank=True, null=True)
    respondent = models.CharField(max_length=50, blank=True, null=True)
    client_type = models.CharField(max_length=50, blank=True, null=True)
    stage_of_case = models.ForeignKey(Case_Stage,on_delete=models.DO_NOTHING, blank=True, null=True)
    fir_number = models.CharField(max_length=50, blank=True, null=True)
    fir_year = models.CharField(max_length=4, blank=True, null=True)
    police_station = models.CharField(max_length=50, blank=True, null=True)
    first_date = models.DateField(blank=True, null=True)
    last_date = models.DateField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    advocate = models.ForeignKey(CustomUser, blank=False, null=False, on_delete=models.CASCADE)
    sub_advocate = models.CharField(max_length=100, null=True,blank=True)
    comments = models.TextField(max_length=50, null=True,blank=True)
    document = models.FileField(upload_to='media/casefiles', blank=True, null=True)
    is_desided = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.petitioner




    
class Clients(BaseModel):
    name = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(max_length=200, blank=True, null=True)
    mobile = models.CharField(max_length=10, blank=True, null=True)
    advocate = models.ForeignKey(CustomUser, blank=False, null=False, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Associate_With_Client(BaseModel):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    case = models.ForeignKey(Case_Master, on_delete=models.CASCADE)

class CaseHistory(BaseModel):
    case = models.ForeignKey(Case_Master,on_delete=models.CASCADE)
    last_date = models.DateField(blank=True,null=True)
    next_date = models.DateField(blank=True,null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)
    particular = models.TextField(max_length=50, blank=True,null=True)
    file = models.FileField(upload_to='media/casefiles', blank=True, null=True)

class CourtTransfer(BaseModel):
    case = models.ForeignKey(Case_Master,on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    old_court = models.CharField(max_length=50, blank=True,null=True)
    new_court = models.CharField(max_length=50, blank=True,null=True)

    
