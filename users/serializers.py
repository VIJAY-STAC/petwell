from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
            'date_of_birth',
            'gender',
            'user_type',
            'location',
            'line_1',
            'line_2',
            'landmark',
            'postal_code',
            'is_active'    
        )




class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
            'date_of_birth',
            'gender',
            'user_type',
            'is_active',
            'location',
            'line_1',
            'line_2',
            'landmark',
            'postal_code'    
        )
