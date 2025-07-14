from django.db import models
from comman_utils.models_constants import *
from orders.models import Orders
from users.models import User

TRAY_STATUS=(
    ('pending','Pending'),
    ('assigned','Assigned'),
    ('picked','Picked'),
    ('checked','Checked'),
    ('packed','Packed'),
)

DUTY_STATUS=(
    ('assined', 'Assigned'),
    ('started', 'Started'),
    ('completed', 'Completed')
)

# Create your models here.
class PickCheckPack(PrimaryUUIDTimeStampedModel,TimeStampedModel):
    tray_no = models.IntegerField(blank=True,null=True)
    order = models.ForeignKey(
        Orders,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pick_order"
    )
    picker= models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="order_picker"
    )
    picked_at = models.DateTimeField(null=True, blank=True)
    checker= models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="order_checker"
    )
    checked_at = models.DateTimeField(null=True, blank=True)
    packer= models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="order_packer"
    )
    packed_at = models.DateTimeField(null=True, blank=True)
    is_finished=models.BooleanField(blank=True, null=True)
    status=models.CharField(max_length=10, null=True, blank=True, choices=TRAY_STATUS)


class Duty(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel):
    name = models.CharField(max_length=30, blank=True, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, null=False, blank=False,choices=DUTY_STATUS, default="placed")