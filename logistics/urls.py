from django.contrib import admin
from django.urls import path,include,re_path
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()
router.register(r"pick_check_pack", PickCheckPackViewSet , basename="pick_check_pack")
router.register(r"duty", DutyViewSet , basename="duty")


urlpatterns = [
     path("api/v1/", include(router.urls)),
]