from rest_framework import serializers
from .models import *
from uuid import uuid4
from datetime import datetime, timezone
from drf_extra_fields.fields import Base64ImageField
from PIL import Image, ImageFile
import io




class ProfileSerializer(serializers.ModelSerializer):
    user_profile_image = serializers.ImageField(required=False)
    class Meta:
        model = CustomUser_JKS
        #fields = '__all__'
        exclude = ['password', 'is_phone_number_verified', 'is_first_login', 'otp', 'otp_created_at']

class UserDetailSerializer(serializers.ModelSerializer):
    jcMobile = ProfileSerializer()
    jcrtMobile = ProfileSerializer()
    
    class Meta:
        model = UserDetail_JKS
        fields = '__all__'



class ImageSerializer(serializers.Serializer):
        jcImage = Base64ImageField()
        jcrtImage = Base64ImageField()
        

class ImageSerializer2(serializers.Serializer):
        image = Base64ImageField()


class ProgramNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProgramName_JKS
        fields = ['id','uid', 'programName','year', 'prog_image', 'prog_expire_date', 'prog_start_date']
    
    
class ProgramImagesSerializer(serializers.ModelSerializer):
    ProgramName = ProgramNameSerializer()
    class Meta:
        model = ProgramImages_JKS
        exclude = ['uid', 'created_at', 'updated_at', 'is_deleted']
    


class BulkImageSerializer(serializers.Serializer):
    images = serializers.ListField(child=ImageSerializer2(), allow_empty=False)

class UserGreetingSerializer(serializers.ModelSerializer):
    #user = ProfileSerializer()
    
    class Meta:
        model = UserGreeting_JKS
        fields = '__all__'