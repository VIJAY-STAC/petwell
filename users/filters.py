import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import User

class UserFilter(django_filters.FilterSet):
    role = filters.CharFilter(field_name="groups__name")
    exclude_user_id = filters.UUIDFilter(field_name="id", exclude=True)

    class Meta:
        model = User
        fields = ["user_type", "is_active", "role", "exclude_user_id"]


