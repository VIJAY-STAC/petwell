from django.conf import settings
from django.db import models
from comman_utils.models_constants import PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel
from users.models import Supplier



class File(PrimaryUUIDTimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=120, null=False, blank=False)
    key = models.CharField(max_length=300, null=True, blank=True)
    url = models.URLField(blank=False, null=False)
    size = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=120, null=False, blank=False)

    def __str__(self):
        return self.url



class Company(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel):
    name = models.CharField(max_length=60, null=False, blank=False)
    image = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="company_image"
    )
    def __str__(self):
        return self.name

class Category(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel):
    name = models.CharField(max_length=60, null=False, blank=False)
    image = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="category_image"
    )
    def __str__(self):
        return self.name
    


class Products(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel):
    name = models.CharField(max_length=60, null=False, blank=False, db_index=True)
    packaging = models.CharField(max_length=10, null=True, blank=True)
    type = models.CharField(max_length=10, null=True, blank=True)
    company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="company"
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="category"
    )
    image = models.ManyToManyField(
        File,
        null=True,
        blank=True,
        related_name="product_image"
    )

    def __str__(self):
        return self.name
    

class Inventory(PrimaryUUIDTimeStampedModel,TimeStampedModel,CreatedByModel):
    product = models.ForeignKey(
        Products,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="product"
    )
    supplier = models.ForeignKey(
        Supplier,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="supplier"
    )
    supplier_scheme= models.CharField(max_length=120, null=True, blank=True)
    dis_scheme= models.DecimalField(max_digits=3, decimal_places=2, null=False, blank=False, default=0.0)
    qty_scheme= models.CharField(max_length=120, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    igst = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    sell_rate = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.0)
    expiry = models.DateTimeField(null=True, blank=True)
    batch = models.CharField(max_length=8, null=True, blank=True)
    stock_in = models.IntegerField(null=False, blank=False, default=0)
    stock_out = models.IntegerField(null=False, blank=False, default=0)
    inventory = models.IntegerField(null=False, blank=False, default=0)
    is_hold = models.BooleanField(default=False, null=False, blank=False)
    is_locked = models.BooleanField(default=False, null=False, blank=False)




