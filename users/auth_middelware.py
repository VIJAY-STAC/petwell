from rest_framework import authentication
from rest_framework import exceptions

from .models import User

from .utils import validate_jwt_token

from django.urls import resolve
from django.http import HttpResponseForbidden
import json
import re

class AuthenticateUser(authentication.BaseAuthentication):
    def authenticate(self, request):
        url_name = resolve(request.path_info).url_name
        if url_name not in ["test_api"]: 
            sql_injection = self.check_sql_injection(request)
            if sql_injection==True:
                raise exceptions.NotAcceptable("Potential SQL injection detected.")
        token = self.get_authorization_header(request)
        if token:
            payload = validate_jwt_token(token)
        else:
            return None
        if payload==None:
            return None
        try:
            user = User.objects.get(id=payload['user_id'], is_active = True) 
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user') 
   
        return (user, None) 

    def get_authorization_header(self, request):
            try:
                header = request.META['HTTP_AUTHORIZATION']
                if not header:
                    return None
                else:
                    parts = header.split()
                    if parts[0].lower() != "jwt":
                        return None
                    elif len(parts) == 1:
                        return None
                    elif len(parts) > 2:
                        return None
                    token = parts[1]
                    return token
            except:
                return None
            
    def contains_sql_injection(self,value):
        sql_keywords = ['SELECT', 'DROP', 'INSERT', 'DELETE', 'UPDATE', 'EXECUTE', 'UNION', 'ALTER', 'CREATE', 'TRUNCATE', 'REPLACE']
        if any(keyword in value.upper() for keyword in sql_keywords):
            return True
        return False
            
    def check_sql_injection(self,request):
        
        for param in request.GET.values():
            if self.contains_sql_injection(param):
                return True
        if request.content_type == 'application/x-www-form-urlencoded':
            for param in request.POST.values():
                if self.contains_sql_injection(param):
                    return True
        elif request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                if isinstance(data, dict):
                    for value in data.values():
                        if isinstance(value, str) and self.contains_sql_injection(value):
                            return True
            except json.JSONDecodeError:
                pass
        return False