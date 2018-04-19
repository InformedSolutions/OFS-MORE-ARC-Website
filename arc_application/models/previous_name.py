from uuid import uuid4
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .application import Application
from .adult_in_home import AdultInHome
from .child_in_home import ChildInHome


class PreviousName(models.Model):
    """
    Model for PREVIOUS_NAME table, used to contain previous
    """
    # Primary Key
    previous_name_id = models.UUIDField(primary_key=True, default=uuid4)

    # Foreign key for both adult an child in home
    adult_id = models.ForeignKey(AdultInHome, null=True, blank=True, on_delete=models.CASCADE)
    child_id = models.ForeignKey(ChildInHome, null=True, blank=True, on_delete=models.CASCADE)

    # Actual name fields
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    @property
    def person(self):
        if self.adult_id is not None:
            return self.adult_id
        if self.child_id is not None:
            return self.child_id
        raise AssertionError("Neither 'adult_id' or 'child_id' is set")
