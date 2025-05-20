from rest_framework import serializers
from v1.models import *
from api.utils import *
from uuid import uuid4
from datetime import datetime, timezone
from api.serializers import StateSerializer, DistrictSerializer



class AdvocateSerializer_MasterAdmin(serializers.ModelSerializer):
    user_state = StateSerializer()
    user_district = DistrictSerializer()

    class Meta:
        
        model = CustomUser
        fields = ["id","first_name","last_name","is_staff","is_active","date_joined","uid","created_at","updated_at",
                  "phone_number","profile_bio","user_profile_image","email","user_type",
                  "user_name","user_dob","user_address1","user_address2","user_address3",
                  "user_district_pincode","advocate_registration_number",
                  "user_under_which_advocate","is_phone_number_verified",
                  "is_email_verified","is_first_login","otp",
                  "otp_created_at","email_token",
                  "email_token_created_at", "last_login", "is_admin", "is_superuser", 
                  "user_id", "user_state", "user_district"]


