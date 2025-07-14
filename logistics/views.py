from django.shortcuts import render
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from datetime import datetime
import uuid
from django.db import transaction
from django.db.models import Sum
import random
from django.core.cache import cache
from django.conf import settings

class PickCheckPackViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    filter_backends = (DjangoFilterBackend,)
    model = PickCheckPack


    @action(detail=False, methods=["get"])
    def pick_check_pack_list(self, request, *args, **kwargs):
        stat = request.query_params.get("stat", None)
        orders = PickCheckPack.objects.all().order_by("created_at")
        if stat:
            orders=orders.filter(status=stat)
        serializers=PickCheckPackListSerializer(orders, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=["post"])
    def tray_assign(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
            return Response({"message":f"Tray in {tray.status} stage."}, status=status.HTTP_200_OK)
        except:
            tray = PickCheckPack.objects.filter(tray_no__isnull=True,is_finished=False).order_by("created_at")
            if not tray:
                return Response({"message":"No order in pending list."}, status=status.HTTP_200_OK)
            tray=tray.first()
            tray.tray_no=tray_no
            tray.picker=request.user
            tray.status="assigned"
            tray.save()
        return Response({"message":"Tray assiged successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def picking_sku_list(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
        except:
            pass
    
        if tray.status!="assigned":
            return Response({"error":f"Tray Status is {tray.status}. Can't pick order in this stage."}, status=status.HTTP_400_BAD_REQUEST)

        serializers = PickingSkuListSerializer(tray)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"])
    def pick_sku(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        sku_id =  request.data.get("sku_id",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
        except:
            return Response({"error":"Tray not found for picking"}, status=status.HTTP_400_BAD_REQUEST)
        
        sku = tray.order.sku_order.all().filter(id=sku_id)
        if not sku:
            return Response({"error":"Sku not found in this tray."}, status=status.HTTP_400_BAD_REQUEST)
        
        sku = sku.first()
        if sku.is_picked==True:
            return Response({"error":"Sku already picked"}, status=status.HTTP_400_BAD_REQUEST)
        sku.picked_qty=sku.placed_qty
        sku.is_picked=True
        sku.save()
        return Response({"message":"sku picked successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"])
    def picking_complete(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
        except:
            return Response({"error":"Tray not found for picking"}, status=status.HTTP_400_BAD_REQUEST)


        skus = tray.order.sku_order.all()
        placed_qty = skus.aggregate(total=Sum("placed_qty"))["total"]
        picked_qty = skus.aggregate(total=Sum("picked_qty"))["total"]

        if placed_qty!=picked_qty:
            return Response({"error":"All skus are not picked."}, status=status.HTTP_400_BAD_REQUEST)
        
        if tray.status!="assigned":
            return Response({"error":f"Tray Status is {tray.status}. Can't complete picking in this stage."}, status=status.HTTP_400_BAD_REQUEST)
        
        tray.picked_at=datetime.now()
        tray.status="picked"
        tray.save()
        return Response({"message":"Picking completed successfully."}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=["get"])
    def checking_sku_list(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
        except:
            pass
    
        if tray.status!="picked":
            return Response({"error":f"Tray Status is {tray.status}. Can't check order in this stage."}, status=status.HTTP_400_BAD_REQUEST)

        serializers = PickingSkuListSerializer(tray)
        tray.checker=request.user
        tray.save()
        return Response(serializers.data, status=status.HTTP_200_OK)



    @action(detail=False, methods=["post"])
    def check_sku(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        sku_id =  request.data.get("sku_id",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
        except:
            return Response({"error":"Tray not found for picking"}, status=status.HTTP_400_BAD_REQUEST)
        
        sku = tray.order.sku_order.all().filter(id=sku_id)
        if not sku:
            return Response({"error":"Sku not found in this tray."}, status=status.HTTP_400_BAD_REQUEST)
        
        sku = sku.first()
        if sku.is_checked==True:
            return Response({"error":"Sku already Checked."}, status=status.HTTP_400_BAD_REQUEST)
        sku.checked_qty=sku.placed_qty
        sku.is_checked=True
        sku.save()
        return Response({"message":"sku Checked successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"])
    def checking_complete(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
        except:
            return Response({"error":"Tray not found for Checking"}, status=status.HTTP_400_BAD_REQUEST)


        skus = tray.order.sku_order.all()
        placed_qty = skus.aggregate(total=Sum("placed_qty"))["total"]
        checked_qty = skus.aggregate(total=Sum("checked_qty"))["total"]

        if placed_qty!=checked_qty:
            return Response({"error":"All skus are not checked."}, status=status.HTTP_400_BAD_REQUEST)
        
        if tray.status!="picked":
            return Response({"error":f"Tray Status is {tray.status}. Can't complete Checking in this stage."}, status=status.HTTP_400_BAD_REQUEST)
        
        tray.checked_at=datetime.now()
        tray.status="checked"
        tray.save()
        return Response({"message":"Checking completed successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def tray_packing(self, request, *args, **kwargs):
        tray_no = request.data.get("tray_no",None)
        if not tray_no:
            return Response({"error":"tray number is requied"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tray = PickCheckPack.objects.get(tray_no=tray_no,is_finished=False)
        except:
            return Response({"error":"Tray not found for Packing."}, status=status.HTTP_400_BAD_REQUEST)

        if tray.status!="checked":
            return Response({"error":f"Tray Status is {tray.status}. Can't Pack tray in this stage."}, status=status.HTTP_400_BAD_REQUEST)
        tray.packed_at=datetime.now()
        tray.is_finished=True
        tray.status="packed"
        tray.packer=request.user
        tray.save()

        order = tray.order
        order.status="packed"
        order.save()
        return Response({"message":"Tray Packed successfully."}, status=status.HTTP_200_OK)
    
class DutyViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    filter_backends = (DjangoFilterBackend,)
    serializer_class=DutyListSerializer
    model = Duty

    def get_queryset(self):
        queryset = Duty.objects.all().order_by("-created_at")
        return queryset

    def create(self, request, *args, **kwargs):
        duty=Duty.objects.create(
            name=datetime.now().date(),
            status="assined",
            created_by=request.user
        )
        serializers = DutyListSerializer(duty)
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        id=kwargs.get("pk")
        try:
            duty=Duty.objects.get(id=id)
        except:
            return Response({"error":"duty not found with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializers =DutyRetrivewSerializer(duty)
        return Response(serializers.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def add_order_to_duty(self, request, *args, **kwargs):
        duty_id=request.data.get("duty_id",None)
        invoice_num=request.data.get("invoice_num",None)

        try:
            duty = Duty.objects.get(id=duty_id)
        except:
            return Response({"error":"duty not found with given id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Orders.objects.get(invoice_number=invoice_num)
        except:
            return Response({"error":"order not found with given invoice number"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        if order.delivery_duty:
            return Response({"error":"Order already added in duty."}, status=status.HTTP_400_BAD_REQUEST)

        
        if order.status!="packed":
            return Response({"error":"Order not ready for delivery."}, status=status.HTTP_400_BAD_REQUEST)
        order.delivery_duty_id=duty_id
        order.out_for_delivery_at=datetime.now()
        order.status="out_for_delivery"
        order.save()
        return Response({"message":"order added in duty."}, status=status.HTTP_200_OK)


    @action(detail=False, methods=["post"])
    def start_duty(self, request, *args, **kwargs):
        duty_id=request.data.get("duty_id",None)
        try:
            duty = Duty.objects.get(id=duty_id)
        except:
            return Response({"error":"duty not found with given id."}, status=status.HTTP_400_BAD_REQUEST)
        if duty.status!="assined":
            return Response({"error":f"duty status {duty.status}. Can't start in this stage."}, status=status.HTTP_400_BAD_REQUEST)

        duty.started_at=datetime.now()
        duty.status="started"
        duty.save()
        return Response({"message":"Duty started successfully."}, status=status.HTTP_200_OK)
        

    @action(detail=False, methods=["post"])
    def deliver_order_otp(self, request, *args, **kwargs):
        invoice_num=request.data.get("invoice_num",None)
        try:
            order = Orders.objects.get(invoice_number=invoice_num)
        except:
            return Response({"error":"order not found with given invoice number"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = random.randint(100000, 999999)
        print("OTP : ", otp)
        cache_key = f"{order.customer.phone_number}#{order.id}#otp"
        cache.set(cache_key,otp,600)
        return Response({"message":"OTP sent on register mobile number"}, status=status.HTTP_200_OK)
        
        


    @action(detail=False, methods=["post"])
    def deliver_order(self, request, *args, **kwargs):
        otp = request.data.get("otp",None)
        invoice_num=request.data.get("invoice_num",None)
        if  otp==None or invoice_num==None:
            return Response({"error":"OTP  and Invoice number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Orders.objects.get(invoice_number=invoice_num)
        except:
            return Response({"error":"order not found with given invoice number"}, status=status.HTTP_400_BAD_REQUEST)
        
        if order.status!="out_for_delivery":
                return Response({"error":f"Order status is {order.status}.Can't delivered order at this stage."}, status=status.HTTP_400_BAD_REQUEST)
           
        cache_key = f"{order.customer.phone_number}#{order.id}#otp"
        cache_value = cache.get(cache_key)
        if not cache_value:
            return Response({"error":"OTP expired."}, status=status.HTTP_400_BAD_REQUEST)
    
        if cache_value==otp:
            order.delivered_at=datetime.now()
            order.status="delivered"
            order.save()
            return Response({"message":"Order delivered to customer."}, status=status.HTTP_200_OK)
        else:
            return Response({"error":"Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        