from datetime import timedelta, time, datetime, date
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from v1.models import *
from api.serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from api.utils import *
from uuid import uuid4
from django.db import transaction
from django.db.models import Max,Min,Q, Count
from django.contrib.auth.hashers import make_password, check_password
from reportlab.pdfgen import canvas
from io import BytesIO
from actbook.serializers import *


class Add_ActBookView(APIView):
    def post(self, request):
        try:
            serializer =actbookSerializer(data = request.data)
            if not serializer.is_valid():
                print(serializer.errors)
                return Response({
                    'status' : 403, 
                    'error': serializer.errors
                    })    
            
            serializer.save()
            return Response({'status' : 200, 'message' : 'Act book created successfully', 'data': serializer.data})
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class ActBookView(APIView):
    def get(self, request):
        try:
            quaryset = actbook.objects.all()
            serializer = actbookSerializer(quaryset, many=True)
            if not serializer.data:
                return Response({'status' : 404, 'message' : 'No act books found'})
            
            return Response({'status' : 200, 'message' : 'Act books retrieved successfully', 'data': serializer.data})
            
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})


class ActBookChapterView(APIView):
    def post(self, request):
        try:
            actbook_id = request.data['actbook_id']
            if actbook_id == 0:
                chapter_objects = actbookchapter.objects.all()
            else:
                chapter_objects = actbookchapter.objects.filter(act__id=actbook_id)
            
            serializer = actbookchapterSerializer(chapter_objects, many=True)
            if not serializer.data:
                return Response({'status' : 404, 'message' : 'No act book chapters found'})
            
            return Response({'status' : 200, 'message' : 'Act book chapters retrieved successfully', 'data': serializer.data})
            
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class ActBookSectionView(APIView):
    def post(self, request):
        try:
            chapter_id = request.data['chapter_id']
            actbook_id = request.data.get('actbook_id', None)

            if actbook_id ==0:
                section_objects = actbooksection.objects.all()
            elif chapter_id == 'all':
                section_objects = actbooksection.objects.filter(chapter__act__id=actbook_id)
            else:
                section_objects = actbooksection.objects.filter(chapter__id=chapter_id)

            serializer = actbooksectionSerializer(section_objects, many=True)
            if not serializer.data:
                return Response({'status' : 404, 'message' : 'No act book sections found'})

            return Response({'status' : 200, 'message' : 'Act book sections retrieved successfully', 'data': serializer.data})


        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class SimilarSectionView(APIView):
    def post(self, request):
        try:
            section_id = request.data['section_id']
            
            similar_section_objects = similarsection.objects.filter(
                Q(section__id=section_id) | Q(similar_section__id=section_id)
            )
            serializer = similarsectionSerializer(similar_section_objects, many=True)
            if not serializer.data:
                return Response({'status' : 404, 'message' : 'No similar sections found'})
            
            return Response({'status' : 200, 'message' : 'Similar sections retrieved successfully', 'data': serializer.data})
            
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})

class SimilarSectionAddView(APIView):
    def post(self, request):
        try:
            section_id = request.data['section_id']
            print(section_id)
            section_obj = actbooksection.objects.get(id=section_id)
            print(section_obj)
            similar_section_id = request.data['similar_section_id']
            print(similar_section_id)
            similar_section_obj = actbooksection.objects.get(id=similar_section_id)
            print(similar_section_obj)
            
            similar_section_obj = similarsection.objects.create(
                section=section_obj,
                similar_section=similar_section_obj
            )
            
            return Response({'status' : 200, 'message' : 'Similar section added successfully'})
        
        except Exception as e:
            print(e)
            return Response({'status' : 404,'message' : 'Something went wrong'})