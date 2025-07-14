from rest_framework import serializers
from .models import *




class OrderCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCart
        fields = (
            "id",
            "inventory",
            "customer",
            "qty"
        )

class OrdersCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = (
            "id",
            "invoice_date",
            "invoice_number",
            "intial_amount",
            "final_amount",
            "status"
        )
        
class OrdersSkusSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name")

    class Meta:
        model = OrdersSkus
        fields = (
            "id",
            "order",
            "inventory",
            "product",
            "placed_qty",
            "delivered_qty",
            "dis_scheme",
            "qty_scheme",
            "cgst",
            "sgst",
            "sell_rate",
            "mrp",
            "expiry",
            "taxable_amt",
            "final_amt"
        )


class OrdersRetrieveSerializer(serializers.ModelSerializer):
    skus = serializers.SerializerMethodField()

    class Meta:
        model = Orders
        fields = (
            "invoice_date",
            "intial_amount",
            "final_amount",
            "status",
            "skus"
        )

    def get_skus(self, obj): 
        skus = obj.sku_order.all()
        return OrdersSkusSerializer(skus, many=True).data
