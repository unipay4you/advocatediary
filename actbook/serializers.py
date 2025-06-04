from rest_framework import serializers
from .models import *
from uuid import uuid4
from datetime import datetime, timezone
from drf_extra_fields.fields import Base64ImageField
from PIL import Image, ImageFile
import io
from actbook.models import *



class actbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = actbook
        fields = '__all__'
        extra_kwargs = {
            'act_name': {'required': True, 'min_length': 3},
            'act_description': {'required': False},
            'act_date_enacted': {'required': False},
            'act_short_name': {'required': True, 'min_length': 3}
        }


    def validate(self, data):  # sourcery skip: extract-method
        if not data.get('act_name'):
            raise serializers.ValidationError("Act name is required.")
        if not data.get('act_description'):
            raise serializers.ValidationError("Act description is required.")
        if not data.get('act_date_enacted'):
            raise serializers.ValidationError("Act date enacted is required.")
        if not data.get('act_short_name'):
            raise serializers.ValidationError("Act short name is required.")
        if actbook.objects.filter(act_name=data['act_name']).exists():
            raise serializers.ValidationError("An act with this name already exists.")
        if actbook.objects.filter(act_short_name=data['act_short_name']).exists():
            raise serializers.ValidationError("An act with this short name already exists.")
        if len(data['act_short_name']) < 3:
            raise serializers.ValidationError("Act short name must be at least 3 characters long.")
        if len(data['act_name']) < 3:
            raise serializers.ValidationError("Act name must be at least 3 characters long.")
        return data
    
    def create(self, validated_data):
        return actbook.objects.create(
            act_name=validated_data['act_name'],
            act_description=validated_data['act_description'],
            act_date_enacted=validated_data['act_date_enacted'],
            act_short_name=validated_data['act_short_name'],
            act_name_hindi=validated_data.get('act_name_hindi', None)
        )

class actbookchapterSerializer(serializers.ModelSerializer):
    act = actbookSerializer()
    class Meta:
        model = actbookchapter
        fields = '__all__'
        extra_kwargs = {
            'act': {'required': True},
            'chapter_number': {'required': True, 'min_value': 1},
            'chapter_title': {'required': True, 'min_length': 3},
            'chapter_title_hindi': {'required': False}
        }

    def validate(self, data):
        if not data.get('act'):
            raise serializers.ValidationError("Act is required.")
        if not data.get('chapter_number'):
            raise serializers.ValidationError("Chapter number is required.")
        if not data.get('chapter_title'):
            raise serializers.ValidationError("Chapter title is required.")
        if actbookchapter.objects.filter(act=data['act'], chapter_number=data['chapter_number']).exists():
            raise serializers.ValidationError("An act chapter with this number already exists for the given act.")
        return data
    
    def create(self, validated_data):
        return actbookchapter.objects.create(
            act=validated_data['act'],
            chapter_number=validated_data['chapter_number'],
            chapter_title=validated_data['chapter_title'],
            chapter_title_hindi=validated_data.get('chapter_title_hindi', None)
        )

class actbooksectionSerializer(serializers.ModelSerializer):
    chapter = actbookchapterSerializer()
    class Meta:
        model = actbooksection
        fields = '__all__'
        extra_kwargs = {
            'chapter': {'required': True},
            'section_number': {'required': True, 'min_length': 1},
            'section_title': {'required': True, 'min_length': 3},
            'section_title_hindi': {'required': False}
        }

    def validate(self, data):
        if not data.get('chapter'):
            raise serializers.ValidationError("Chapter is required.")
        if not data.get('section_number'):
            raise serializers.ValidationError("Section number is required.")
        if not data.get('section_title'):
            raise serializers.ValidationError("Section title is required.")
        if actbooksection.objects.filter(chapter=data['chapter'], section_number=data['section_number']).exists():
            raise serializers.ValidationError("An act section with this number already exists for the given chapter.")
        return data
    
    def create(self, validated_data):
        return actbooksection.objects.create(
            chapter=validated_data['chapter'],
            section_number=validated_data['section_number'],
            section_title=validated_data['section_title'],
            section_title_hindi=validated_data.get('section_title_hindi', None)
        )

class similarsectionSerializer(serializers.ModelSerializer):
    section = actbooksectionSerializer()
    similar_section = actbooksectionSerializer()

    class Meta:
        model = similarsection
        fields = '__all__'
        extra_kwargs = {
            'section': {'required': True},
            'similar_section_number': {'required': True, 'min_length': 1},
            'similar_section_title': {'required': True, 'min_length': 3},
            'similar_section_title_hindi': {'required': False}
        }

    def validate(self, data):
        if not data.get('section'):
            raise serializers.ValidationError("Section is required.")
        if not data.get('similar_section_number'):
            raise serializers.ValidationError("Similar section number is required.")
        if not data.get('similar_section_title'):
            raise serializers.ValidationError("Similar section title is required.")
        if similarsection.objects.filter(section=data['section'], similar_section_number=data['similar_section_number']).exists():
            raise serializers.ValidationError("A similar section with this number already exists for the given section.")
        return data
    
    def create(self, validated_data):
        return similarsection.objects.create(
            section=validated_data['section'],
            similar_section_number=validated_data['similar_section_number'],
            similar_section_title=validated_data['similar_section_title'],
            similar_section_title_hindi=validated_data.get('similar_section_title_hindi', None)
        )