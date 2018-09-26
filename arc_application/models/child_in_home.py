import datetime
from django.db import models
from .childbase import ChildBase


class ChildInHome(ChildBase):
    """
    Model for CHILD_IN_HOME table
    """
    relationship = models.CharField(max_length=100, blank=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    @property
    def timelog_fields(self):
        """
        Specify which fields to track in this model once application is returned.

        Used for signals only. Check base.py for available signals.
        This is used for logging fields which gonna be updated by applicant
        once application status changed to "FURTHER_INFORMATION" on the arc side

        Returns:
            tuple of fields which needs update tracking when application is returned
        """

        return (
            'child',
            'first_name',
            'middle_names',
            'last_name',
            'birth_day',
            'birth_month',
            'birth_year',
            'relationship'
        )

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

    def get_summary_table(self):

        if self.birth_day < 10:
            birth_day = '0' + str(self.birth_day)
        else:
            birth_day = str(self.birth_day)

        if self.birth_month < 10:
            birth_month = '0' + str(self.birth_month)
        else:
            birth_month = str(self.birth_month)

        date_of_birth = birth_day + ' ' + birth_month + ' ' + str(self.birth_year)

        return [
            {"title": self.get_full_name(), "id": self.pk},
            {"name": "Name", "value": self.get_full_name()},
            {"name": "Date of birth", "value": date_of_birth},
            {"name": "Relationship", "value": self.relationship}
        ]

    # Date of birth property created to keep DRY
    @property
    def date_of_birth(self):
        return datetime(year=self.birth_year, month=self.birth_month, day=self.birth_day)

    class Meta:
        db_table = 'CHILD_IN_HOME'
