from django.contrib import admin
from django.urls import path,include,re_path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"orders", OrdersViewSet , basename="orders")
router.register(r"cart", OrdersCartViewSet , basename="cart")

urlpatterns = [
     path("api/v1/", include(router.urls)),
]