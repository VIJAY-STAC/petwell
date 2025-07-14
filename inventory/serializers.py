from rest_framework import serializers
from .models import *


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name"
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name"
        )

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = (
            "id",
            "name",
            "packaging",
            "type",
            "company",
            "category", 
        )

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = (
            "id",
            "product",
            "supplier",
            "supplier_scheme",
            "dis_scheme",
            "qty_scheme",
            "purchase_rate",
            "sell_rate", 
            "mrp",
            "expiry",
            "batch",
            "stock_in",
            "stock_out",
            "inventory",
            "is_hold",
            "is_locked",
            "sgst",
            "cgst"
        )


class GetStockSerializer(serializers.ModelSerializer):
    p_name = serializers.CharField(source="product.name")
    class Meta:
        model = Inventory
        fields = (
            "id",
            "p_name",
            "supplier_scheme",
            "dis_scheme",
            "qty_scheme",
            "sell_rate", 
            "mrp",
            "expiry",
            "batch",
            "inventory"
        )
