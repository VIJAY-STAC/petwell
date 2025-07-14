from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db.models import PointField
from phonenumber_field.modelfields import PhoneNumberField
from comman_utils.models_constants import PrimaryUUIDTimeStampedModel, TimeStampedModel,CreatedByModel
import hashlib

GENDERS = (("male", "Male"), ("female", "Female"), ("other", "Other"))
USER_TYPES = (("admin", "Admin"), ("billing", "Billing"), ("logistic", "Logistic"),("customer","Customer"),("supplier","Supplier"))

class User(AbstractUser, PrimaryUUIDTimeStampedModel):
    name = models.CharField("Name of User", blank=True, max_length=255)
    phone_number = PhoneNumberField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        null=False, blank=False, max_length=6, choices=GENDERS, default="other"
    )
    user_type = models.CharField(
        null=False, blank=False, max_length=32, choices=USER_TYPES
    )
    location = PointField(null=True, blank=True)
    line_1 = models.CharField(max_length=512,null=True, blank=True)
    line_2 = models.CharField(max_length=512, null=True, blank=True)
    landmark = models.CharField(blank=True, max_length=100)
    postal_code = models.CharField(max_length=16, blank=True)

    @property
    def full_name(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name, last_name=self.last_name
        )

    def __str__(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name, last_name=self.last_name
        )
    
class Supplier(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel):
        name = models.CharField( blank=False, null=False, max_length=255)
        location = PointField(null=True, blank=True)
        line_1 = models.CharField(max_length=512,null=True, blank=True)
        line_2 = models.CharField(max_length=512, null=True, blank=True)
        landmark = models.CharField(blank=True, max_length=100)
        postal_code = models.CharField(max_length=16, blank=True)
        user = models.ForeignKey(
                User,
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name="supplier_user"
        )
