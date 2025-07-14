from django.shortcuts import render
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *

class CompanyViewSet(viewsets.ModelViewSet):
        serializer_class = CompanySerializer
        permission_classes = (permissions.IsAuthenticated,)
        model=Company
        def get_queryset(self):
                queryset = Company.objects.all().order_by("name")
                return queryset
        
class CategoryViewSet(viewsets.ModelViewSet):
        serializer_class = CategorySerializer
        permission_classes = (permissions.IsAuthenticated,)
        model=Category
        def get_queryset(self):
            queryset = Category.objects.all().order_by("name")
            return queryset

class ProductViewSet(viewsets.ModelViewSet):
        serializer_class = ProductsSerializer
        permission_classes = (permissions.IsAuthenticated,)
        model=Products

        def get_queryset(self):
            queryset = Products.objects.all().order_by("name")
            return queryset


# Create your views here.
class InventoryViewSet(viewsets.ModelViewSet):
        model=Inventory
        serializer_class = InventorySerializer
        parser_classes = (parsers.FormParser, parsers.JSONParser)
        filter_backends = (DjangoFilterBackend,)
        permission_classes = (permissions.IsAuthenticated,)
       
        def get_queryset(self):
            queryset = Inventory.objects.select_related("product").order_by("product__name")
            return queryset
        

        def create(self, request, *args, **kwargs):
                data = request.data
                serializer  = InventorySerializer(data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(created_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:  
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        def update(self, request, *args, **kwargs):
                id = kwargs.get("pk", None)
                if not id:
                    return Response({"error":"id is required"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    invetory = Inventory.objects.get(id=id)
                except:
                    return Response({"error":"inventory not found with given id."}, status=status.HTTP_400_BAD_REQUEST)
            
                serializers = InventorySerializer(invetory, data=request.data, partial=True )
                if serializers.is_valid(raise_exception=True):
                    serializers.save()
                    return Response(serializers.data, status=status.HTTP_201_CREATED)
                else:  
                    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
                
        def destroy(self, request, *args, **kwargs):
                return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                

        @action(detail=False, methods=["get"])
        def get_avail_stock(self, request, *args, **kwargs):
            queryset = Inventory.objects.select_related("product").filter(is_hold=False,is_locked=False,inventory__gt=0).order_by("-inventory")
            serializers = GetStockSerializer(queryset, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
            
