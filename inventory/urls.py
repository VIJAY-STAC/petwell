from django.contrib import admin
from django.urls import path,include,re_path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"company", CompanyViewSet , basename="company")
router.register(r"category", CategoryViewSet , basename="category")
router.register(r"products", ProductViewSet , basename="products")
router.register(r"inventory", InventoryViewSet , basename="inventory")

urlpatterns = [
     path("api/v1/", include(router.urls)),
]