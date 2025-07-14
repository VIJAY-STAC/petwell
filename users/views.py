from django.shortcuts import render
from rest_framework import parsers, status, permissions, viewsets
import random
from .utils import generate_jwt_token
from .models import User
from .filters import UserFilter
from .serializers import UserSerializer, UserListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
import uuid
import string
from django.utils.crypto import get_random_string
from django.core.cache import cache

class UserViewSet(viewsets.ModelViewSet):
        serializer_class = UserSerializer
        parser_classes = (parsers.FormParser, parsers.JSONParser)
        filter_backends = (DjangoFilterBackend,)
        filterset_class = UserFilter
        permission_classes = (permissions.IsAuthenticated,)
        model=User

        def get_queryset(self):
                queryset = User.objects.all().order_by("-created_at")
                return queryset

        @action(detail=False, methods=["get"],permission_classes=[] )
        def test_api(self, request, *args, **kwargs):
                return Response({"message":"user test api working"}, status=status.HTTP_200_OK)
        
        def create(self,  request, *args, **kwargs):
                data = request.data
                lat=data.get("lat",None)
                long=data.get("long",None)
                if lat and long:
                        locaion = Point(float(long), float(lat))
                        data["locaion"]=locaion
                if data.get("user_type")=="customer":
                        username=data.get("phone_number")
                else:
                        username=data.get("email")

                data["username"]=username
                serializer = UserSerializer(data=data)
                if serializer.is_valid():
                        user = serializer.save()
                        serializ = UserListSerializer(user)
                        return Response(serializ.data, status=status.HTTP_200_OK)
                else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        

        def update(self,  request, *args, **kwargs):
                data = request.data
                pk=kwargs.get("pk")
                try:
                        user = User.objects.get(id=pk)
                except:
                        return Response({"error":"user not found with given id."}, status=status.HTTP_400_BAD_REQUEST)
                serializer = UserSerializer(user, data=data, partial=True)
                if serializer.is_valid():
                        serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
        
        def destroy(self, request, *args, **kwargs):
                return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        

        @action(detail=False, methods=["post"], permission_classes=[])
        def forgot_password(self, request, *args, **kwargs):
                username = request.data.get("username",None)
                try:
                        user=User.objects.get(username=username)
                except:
                        return Response({"error":"user doest not found with username"}, status=status.HTTP_400_BAD_REQUEST)
                otp = get_random_string(length=6, allowed_chars=string.digits)
                print("otp",otp)
                key = f"{user.id}#otp"
                cache.set(key,otp,timeout=600)
                return Response({"message":"opt sent to registered email id"}, status=status.HTTP_200_OK)
        
        @action(detail=False, methods=["post"], permission_classes=[])
        def otp_verify(self, request, *args, **kwargs):
                username = request.data.get("username",None)
                otp = request.data.get("otp",None)
                if not otp:
                        return Response({"error":"please enter a otp"}, status=status.HTTP_400_BAD_REQUEST)
                user=User.objects.get(username=username)
                key = f"{user.id}#otp"
                set_otp = cache.get(key,None)
                if not set_otp:
                        return Response({"error":"opt expired."}, status=status.HTTP_400_BAD_REQUEST)

                print(otp)
                print(set_otp)

                if set_otp!=otp:
                        return Response({"error":"Invalid opt."}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({"username":username}, status=status.HTTP_200_OK)


        @action(detail=False, methods=["post"], permission_classes=[])
        def set_password(self, request, *args, **kwargs):
                username = request.data.get("username",None)
                new_password = request.data.get("new_password",None)
                confirm_password = request.data.get("confirm_password",None)
                if new_password!=confirm_password:
                        return Response({"error":"new password and confirm password should be same."}, status=status.HTTP_400_BAD_REQUEST)
                user=User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                return Response({"message":"Password set successfully"}, status=status.HTTP_200_OK)
        
        
        @action(detail=False, methods=["post"], permission_classes=[])
        def login(self, request, *args, **kwargs):
                username = request.data.get("username", None)
                password = request.data.get("password", None)

                if not username or not password:
                        return Response({"error":"username and password is reqiured"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                        user=User.objects.get(username=username)
                except:
                        return Response({"error":"username does not exist with given username"}, status=status.HTTP_400_BAD_REQUEST)
                if not user.check_password(password):
                        return Response("incorrect_credentials", status=status.HTTP_400_BAD_REQUEST)
                token=generate_jwt_token(str(user.id),user.user_type)
                print("toekn", token)
                serializer = UserListSerializer(user)
                res = serializer.data
                res["token"]=token
                return Response(res, status=status.HTTP_200_OK)
                
                
                

