from django.db import models
from django.contrib.auth.models import AbstractUser
from v1.manager import UserManager
import uuid
from django.utils.text import slugify
import random
from django.contrib.auth.hashers import make_password

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


    

class CustomUser_JKS(BaseModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    user_profile_image = models.ImageField(upload_to='media/JKS/profile_image', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    USERNAME_FIELD = 'phone_number'
    user_type_choices = (
        ('admin', 'admin'),
        ('member', 'member'),
        ('user', 'user'),
    )
    user_type = models.CharField(max_length=10, choices=user_type_choices, default='member')
    user_name = models.CharField(max_length=100, blank=True, null=True)
    user_dob = models.DateField(blank=True,null=True)
    user_address1 = models.CharField(max_length=100, blank=True, null=True)
    user_address2 = models.CharField(max_length=100, blank=True, null=True)
    user_address3 = models.CharField(max_length=100, blank=True, null=True)
    
    user_state = models.CharField(max_length=100, blank=True, null=True)
    user_district = models.CharField(max_length=100, blank=True, null=True)
    user_district_pincode = models.IntegerField(blank=True, null=True)
    is_phone_number_verified = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    mobile_number_belongs_to = models.CharField(max_length=15, blank=True, null=True)
    
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.phone_number
    

class UserDetail_JKS(BaseModel):
    jcName = models.CharField(max_length=100, blank=True, null=True)
    jcMobile = models.ForeignKey(CustomUser_JKS, on_delete=models.CASCADE, blank=True, null=True, related_name='jcMobile')
    jcrtName = models.CharField(max_length=100, blank=True, null=True)
    jcrtMobile = models.ForeignKey(CustomUser_JKS, on_delete=models.CASCADE, blank=True, null=True, related_name='jcrtMobile')
    anniversaryDate = models.DateField(blank=True, null=True)
    jcDob = models.DateField(blank=True, null=True)
    jcrtDob = models.DateField(blank=True, null=True)
    jcQualification = models.CharField(max_length=100, blank=True, null=True)
    jcBloodGroup = models.CharField(max_length=10, blank=True, null=True)
    jcEmail = models.EmailField(blank=True, null=True)
    jcHomeAddress = models.CharField(max_length=100, blank=True, null=True)
    jcOccupation = models.CharField(max_length=100, blank=True, null=True)
    jcFirmName = models.CharField(max_length=100, blank=True, null=True)
    jcOccupationAddress = models.CharField(max_length=100, blank=True, null=True)
    jcrtBloodGroup = models.CharField(max_length=10, blank=True, null=True)
    jcrtEmail = models.EmailField(blank=True, null=True)
    jcrtOccupation = models.CharField(max_length=100, blank=True, null=True)
    jcrtOccupationAddress = models.CharField(max_length=100, blank=True, null=True)
    jcpost = models.CharField(max_length=100, blank=True, null=True)
    jcrtpost = models.CharField(max_length=100, blank=True, null=True)
    jcImage = models.ImageField(upload_to='media/JKS/profile_image', blank=True, null=True)
    jcrtImage = models.ImageField(upload_to='media/JKS/profile_image', blank=True, null=True)
    searchteg = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)


class ProgramName_JKS(BaseModel):
    programName = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=4, null=True, blank=True)
    prog_image = models.ImageField(upload_to='media/JKS/program_images', blank=True, null=True)
    prog_expire_date = models.DateField(blank=True, null=True)
    prog_start_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.programName

class ProgramImages_JKS(BaseModel):
    ProgramName = models.ForeignKey(ProgramName_JKS, on_delete=models.CASCADE,blank=True,null=True)
    image = models.ImageField(upload_to='media/JKS/program_images', blank=True, null=True)


class UserGreeting_JKS(BaseModel):
    user = models.ForeignKey(CustomUser_JKS, on_delete=models.CASCADE, blank=True, null=True)
    greeting_image = models.ImageField(upload_to='media/JKS/greeting_images', blank=True, null=True)
    image_position_x = models.CharField(max_length=100, blank=True, null=True)
    image_position_y = models.CharField(max_length=100, blank=True, null=True)
    image_width = models.CharField(max_length=100, blank=True, null=True)
    image_height = models.CharField(max_length=100, blank=True, null=True)
    image_rotation = models.CharField(max_length=100, blank=True, null=True)
    image_scale = models.CharField(max_length=100, blank=True, null=True)
    name_position_x = models.CharField(max_length=100, blank=True, null=True)
    name_position_y = models.CharField(max_length=100, blank=True, null=True)
    name_width = models.CharField(max_length=100, blank=True, null=True)
    name_height = models.CharField(max_length=100, blank=True, null=True)
    name_rotation = models.CharField(max_length=100, blank=True, null=True)
    name_scale = models.CharField(max_length=100, blank=True, null=True)
    greeting_image_choice = (
        ('birthday', 'Birthday'),
        ('anniversary', 'Anniversary'),
    )
    greeting_image_type = models.CharField(max_length=100, choices=greeting_image_choice, blank=True, null=True)
    

