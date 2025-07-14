import uuid
from django.db import models
from django.conf import settings

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True



class PrimaryUUIDModel(models.Model):
    # id = models.AutoField(primary_key=True,)
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    
    class Meta(object):
        abstract = True


class PrimaryUUIDTimeStampedModel(PrimaryUUIDModel, TimeStampedModel):
    class Meta(object):
        abstract = True


class CreatedByModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created_by",
    )

    class Meta(object):
        abstract = True


class LastModifiedByModel(models.Model):
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_last_modified_by",
    )

    class Meta(object):
        abstract = True