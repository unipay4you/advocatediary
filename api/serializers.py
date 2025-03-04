from rest_framework import serializers
from v1.models import *
from api.utils import *
from uuid import uuid4
from datetime import datetime, timezone


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

        if len(data['password']) < 8:
            raise serializers.ValidationError({'error':'Password should be minimum 8 digit and alph numeric with atleast one capital and one lower latter with atleast one special charector'})

        if data['password']:
            special_characters = "!@#$%^&*()-+?_=,<>/"
            is_special_digit_exist = any(
                (c in special_characters for c in data['password'])
            )
            is_numeric_digit_exist = any(n.isdigit() for n in data['password'])
            is_capital_digit_exist = any(n.isupper() for n in data['password'])
            is_lower_digit_exist = any(n.islower() for n in data['password'])
            if not (is_lower_digit_exist & is_capital_digit_exist & is_numeric_digit_exist & is_special_digit_exist):
                raise serializers.ValidationError({'error':'Password should be minimum 8 digit and alph numeric with atleast one capital and one lower latter with atleast one special charector'})
        return data
    
    def create(self, validated_data):
        email_token = uuid4()
        otp = random.randint(100001, 999999)
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





































    

class CourtSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Court
        fields = '__all__'

class CaseSerializer(serializers.ModelSerializer):
    #advocate = UserSerializer()
    class Meta:
        model = CustomUser
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District    
        fields = '__all__'


class case_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case_Type  
        fields = '__all__'


class stage_of_caseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case_Stage   
        fields = '__all__'

