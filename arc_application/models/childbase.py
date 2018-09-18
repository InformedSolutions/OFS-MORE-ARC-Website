import datetime
from uuid import uuid4
from django.db import models
from .application import Application


class ChildBase(models.Model):
    """
    Model for CHILD_IN_HOME table
    """
    child_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    child = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_day = models.IntegerField(blank=True)
    birth_month = models.IntegerField(blank=True)
    birth_year = models.IntegerField(blank=True)

    def get_full_name(self):
        if len(self.middle_names) > 0:
            concatenated_name = self.first_name + " " \
                                + self.middle_names + " " + self.last_name
        else:
            concatenated_name = self.first_name + " " + self.last_name

        return concatenated_name

    def get_dob_as_date(self):
        return datetime.date(self.birth_year, self.birth_month, self.birth_day)

    class Meta:
        abstract = True
