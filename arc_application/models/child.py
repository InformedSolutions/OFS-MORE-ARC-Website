import datetime
from django.db import models

from .childbase import ChildBase


class Child(ChildBase):
    """
    Model for CHILD table
    """
    lives_with_childminder = models.NullBooleanField(blank=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_full_name(self):
        """
        Helper method for retrieving a full name from its constituent parts
        :return: the full name for a child
        """
        return ' '.join([self.first_name, (self.middle_names or ''), self.last_name])

    def get_dob_as_date(self):
        """
        Helper method for retrieving an adult's date of birth as a datetime object
        :return: the adult's date of birth as a datetime object
        """
        return datetime.date(self.birth_year, self.birth_month, self.birth_day)

    class Meta:
        db_table = 'CHILD'
