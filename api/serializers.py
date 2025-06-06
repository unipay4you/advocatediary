from rest_framework import serializers
from v1.models import *
from api.utils import *
from uuid import uuid4
from datetime import datetime, timezone



class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'
        
class DistrictSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    class Meta:
        model = District    
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser    
        fields = ['user_name', 'phone_number', 'password', 'email']


    def validate(self, data):  # sourcery skip: extract-method
      
        if len(data['phone_number']) != 10:
            raise serializers.ValidationError({'error':'Mobile number should be 10 digit'})

        if data['phone_number']:
            for n in data['phone_number']:
                if not n.isdigit():
                    raise serializers.ValidationError({'error':'Mobile number should be numeric'})
        
        if 'user_name' not in data:
            raise serializers.ValidationError({'error':'Name required'})

        if data['user_name']:
            for n in data['user_name']:
                if n.isdigit():
                    raise serializers.ValidationError({'error':'Name should be alphabatic'})

        if 'email' not in data:
            raise serializers.ValidationError({'error':'email required'})

        if 'password' not in data:
            raise serializers.ValidationError({'error':'password required'})

        if len(data['password']) < 6:
            raise serializers.ValidationError({'error':'Password should be minimum 6 digit'})

        return data
    
    def create(self, validated_data):
        email_token = uuid4()
        otp = generate_otp()
        otp_msg = f'Your account verification OTP is {otp}'
        
        
        user = CustomUser.objects.create(
            user_name = validated_data['user_name'],
            phone_number = validated_data['phone_number'],
            email = validated_data['email'],
            email_token = email_token,
            email_token_created_at = datetime.now(timezone.utc),
            otp = otp,
            otp_created_at = datetime.now(timezone.utc),
            )
        user.set_password(validated_data['password'])
        user.save()

        send_email_token((validated_data['email']), email_token)
        send_msg_to_mobile(validated_data['phone_number'], otp, otp_msg)

        return user

class PasswordChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser    
        fields = ['phone_number', 'password']


    def validate(self, data):  # sourcery skip: extract-method
      
        if len(data['phone_number']) != 10:
            raise serializers.ValidationError({'error':'Mobile number should be 10 digit'})

        if data['phone_number']:
            for n in data['phone_number']:
                if not n.isdigit():
                    raise serializers.ValidationError({'error':'Mobile number should be numeric'})
        
        if 'password' not in data:
            raise serializers.ValidationError({'error':'password required'})

        if len(data['password']) < 6:
            raise serializers.ValidationError({'error':'Password should be minimum 6 digit'})

        return data
    
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({'error':'Password required'})


class ProfileSerializer(serializers.ModelSerializer):
    user_state = StateSerializer()
    user_district = DistrictSerializer()
    class Meta:
        model = CustomUser
        #field = '--all--'
        fields = ["id","phone_number","user_profile_image","email","user_type","user_name","user_dob","user_address1",
                  "user_address2","user_address3","user_district_pincode","advocate_registration_number","user_under_which_advocate",
                  "is_phone_number_verified","is_email_verified","is_first_login","user_state","user_district", "is_admin","is_superuser"]



class AdvocateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id","phone_number","user_name"]


class StageOfCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case_Stage   
        fields = '__all__'
        #["id","is_deleted", "crn","case_no","case_year","state","district","court_type","court_name",
         #         "court_no","under_section","petitioner","respondent","client_type","fir_number","fir_year",
          #        "police_station","first_date","last_date","next_date","sub_advocate","comments","document","is_desided","is_active","case_type","stage_of_case","advocate"]


class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case_Type  
        fields = '__all__'


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court  
        fields = '__all__'

class CaseSerializer(serializers.ModelSerializer):
    advocate = AdvocateSerializer()
    stage_of_case = StageOfCaseSerializer()
    case_type = CaseTypeSerializer()
    court_id = CourtSerializer()
    class Meta:
        model = Case_Master
        fields = '__all__'
       

class CaseByIDSerializer(serializers.ModelSerializer):
    advocate = AdvocateSerializer()
    stage_of_case = StageOfCaseSerializer()
    case_type = CaseTypeSerializer()
    class Meta:
        model = Case_Master
        fields = '__all__'


class CaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseHistory  
        fields = '__all__'

class CourtTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Court_Type
        fields = '__all__'

class CourtSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    court_type = CourtTypeSerializer()
    class Meta:
        model = Court
        fields = '__all__'


class AndoidAppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Andoid_app_version
        fields = '__all__'
