from django.db import models
from comman_utils.models_constants import *
from inventory.models import Inventory,Products
from users.models import User

ORDER_STATUS=(
    ('placed','Placed'),
    ('packed','Packed'),
    ('picked','Picked'),
    ('out_for_delivery','Out For Delivery'),
    ('delivered','Delivered'),
    ('cancelled','Cancelled'),
    ('return_initiated','Return Initiated'),
    ('return_received','Return Received'),
    ('refunded','Refunded'),
)

class OrderCart(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel):
    inventory = models.ForeignKey(
        Inventory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cart_inventory"
    )
    customer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cart_user"
    )
    qty = models.IntegerField( null=False, blank=False)


class Orders(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel, LastModifiedByModel):
    invoice_date = models.DateTimeField(null=False, blank=False)
    invoice_number = models.CharField(max_length=10, null=False, blank=False)
    intial_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    status = models.CharField(max_length=20, null=False, blank=False,choices=ORDER_STATUS, default="placed")
    delivered_at = models.DateTimeField(null=True, blank=True) 
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    customer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="customer_user"
    )
    delivery_duty = models.ForeignKey(
        "logistics.Duty",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="delivery_duty"
    )
   
    


class OrdersSkus(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel, LastModifiedByModel):
    order = models.ForeignKey(
        Orders,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sku_order"
    )
    inventory = models.ForeignKey(
        Inventory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sku_inventory"
    )
    product = models.ForeignKey(
        Products,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sku_product"
    )
    placed_qty = models.IntegerField(null=True, blank=True, default=0)
    delivered_qty = models.IntegerField(null=True, blank=True, default=0)
    supplier_scheme= models.CharField(max_length=120, null=True, blank=True)
    dis_scheme= models.CharField(max_length=120, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    igst = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    qty_scheme= models.CharField(max_length=120, null=True, blank=True)
    sell_rate = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    expiry = models.DateTimeField(null=True, blank=True)
    taxable_amt = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    final_amt = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    is_picked = models.BooleanField(blank=True, null=True, default=False)
    picked_qty = models.IntegerField(null=True, blank=True, default=0)
    is_checked = models.BooleanField(blank=True, null=True, default=False)
    checked_qty = models.IntegerField(null=True, blank=True, default=0)
    is_packed = models.BooleanField(blank=True, null=True, default=False)
    is_cancelled = models.BooleanField(null=False, blank=False, default=False)
