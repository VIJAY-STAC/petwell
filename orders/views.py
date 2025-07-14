from django.shortcuts import render
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from logistics.models import PickCheckPack
from .models import *
from .serializers import *
from datetime import datetime
import uuid
from django.db import transaction

class OrdersViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrdersCreateSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    filter_backends = (DjangoFilterBackend,)
    model=Orders

    def get_queryset(self):
        queryset = Orders.objects.all().order_by("-created_at")
        return queryset
    

    def create(self, request, *args, **kwargs):
        c_id = request.data.get("customer_id", None)
        if not c_id:
            return Response({"error": "Customer id required"}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = OrderCart.objects.select_related("inventory", "inventory__product").filter(customer_id=c_id)
        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        intial_amount = 0.0
        final_amount = 0.0

        osku_bulk_create = []
        update_inventory = []

        with transaction.atomic():
            for item in cart_items:
                inventory_stock = item.inventory
                inventory_stock.stock_out += item.qty
                inventory_stock.inventory -= item.qty
                update_inventory.append(inventory_stock)

                intial_amount += float(((item.inventory.sell_rate) * (1 + item.inventory.gst/100)) * item.qty)
                taxable_amt = float(((item.inventory.sell_rate)* (1 - (item.inventory.dis_scheme / 100))) * item.qty)
                final_amt = taxable_amt * float((1 + (item.inventory.gst/100)))
                final_amount += final_amt

            
            lates_num=Orders.objects.all().order_by("-created_at").first()
            _,num = lates_num.invoice_number.split("-")

            # Create order FIRST and get the saved object
            order_data = {
                "invoice_date": datetime.now(),
                "intial_amount": intial_amount,
                "invoice_number":f"P-{num+1}",
                "final_amount": final_amount,
                "status": "placed"
            }

            serializer = OrdersCreateSerializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            order_obj = serializer.save(created_by=request.user)  # <-- get the actual saved object with UUID

            # Now use order_obj.id
            for item in cart_items:
                osku_bulk_create.append(OrdersSkus(
                    order_id=order_obj.id,
                    inventory_id=item.inventory_id,
                    product_id=item.inventory.product_id,
                    placed_qty=item.qty,
                    supplier_scheme=item.inventory.supplier_scheme,
                    dis_scheme=item.inventory.dis_scheme,
                    cgst=item.inventory.cgst,
                    sgst=item.inventory.sgst,
                    igst=item.inventory.sgst,
                    qty_scheme=item.inventory.qty_scheme,
                    sell_rate=item.inventory.sell_rate,
                    mrp=item.inventory.mrp,
                    expiry=item.inventory.expiry,
                    taxable_amt=float(((item.inventory.sell_rate) * (1 - (item.inventory.dis_scheme / 100))) * item.qty),
                    final_amt=float(((item.inventory.sell_rate) *(1 - (item.inventory.dis_scheme / 100))) * item.qty) * float((1 + item.inventory.gst/100)),
                    is_cancelled=False
                ))

            OrdersSkus.objects.bulk_create(osku_bulk_create)
            Inventory.objects.bulk_update(update_inventory, ["stock_out", "inventory"])
            PickCheckPack.objects.create(order=order_obj,status="pending",is_finished=False)
            cart_items.delete()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        id=kwargs.get("pk")
        try:
            order=Orders.objects.get(id=id)
        except:
            return Response({"error":"Order not found with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializers =OrdersRetrieveSerializer(order)
        return Response(serializers.data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
class OrdersCartViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrderCartSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    filter_backends = (DjangoFilterBackend,)
    model=OrderCart

    def get_queryset(self):
        queryset = OrderCart.objects.all().order_by("-created_at")
        return queryset
    
    def create(self, request, *args, **kwargs):
        data = request.data
        data["customer"]=request.user.id
        serializer  = OrderCartSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def list(self, request, *args, **kwargs):
        customer_id = request.user.id
        items=OrderCart.objects.filter(customer_id=customer_id)
        serializers =OrderCartSerializer(items, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
        
    def update(self, request, *args, **kwargs):
        id=kwargs.get("pk")
        new_qty = request.data.get("qty",None)
        try:
            cart_item=OrderCart.objects.get(id=id)
        except:
            return Response({"error":"cart_item not found with given id."}, status=status.HTTP_400_BAD_REQUEST)
        if new_qty<=0:
            cart_item.delete()
            return Response({"message":"cart item removed successfully."}, status=status.HTTP_200_OK)

        cart_item.qty= new_qty
        cart_item.save()
        serializers =OrderCartSerializer(cart_item)
        return Response(serializers.data, status=status.HTTP_200_OK)

       