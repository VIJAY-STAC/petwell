from rest_framework import serializers

from orders.models import OrdersSkus, Orders
from .models import *


class MiniSkuListSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name")
    class Meta:
        model = OrdersSkus
        fields = (
            "id",
            "product",
            "placed_qty",
            "picked_qty",
            "checked_qty",
            "mrp",
            "expiry"
        )




class PickCheckPackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickCheckPack
        fields = (
            "tray_no",
            "order",
            "status"
        )

class PickingSkuListSerializer(serializers.ModelSerializer):
    skus = serializers.SerializerMethodField()
    class Meta:
        model = PickCheckPack
        fields = (
            "tray_no",
            "skus",
        )
    def get_skus(self, obj): 
        skus = obj.order.sku_order.all()
        return MiniSkuListSerializer(skus, many=True).data


class DutyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Duty
        fields = (
            "id",
            "name",
            "started_at",
            "completed_at",
            "status"
        )


class MiniOrderSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer.full_name')
    mo_num = serializers.CharField(source='customer.phone_number')
    location = serializers.CharField(source='customer.location')
    address = serializers.SerializerMethodField()
    class Meta:
        model = Orders
        fields = (
            "invoice_number",
            "final_amount",
            "status",
            "customer",
            "status",
            "mo_num",
            "address",
            "location"
        )
    def get_address(self, obj):
        add = f"{obj.customer.line_1}, {obj.customer.line_2} , {obj.customer.landmark}, {obj.customer.postal_code}"
        return add

    


class DutyRetrivewSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()
    class Meta:
        model = Duty
        fields = (
            "name",
            "started_at",
            "completed_at",
            "status",
            "orders"
        )

    def get_orders(self, obj):
        orders  = obj.delivery_duty.all()
        return MiniOrderSerializer(orders, many=True).data

