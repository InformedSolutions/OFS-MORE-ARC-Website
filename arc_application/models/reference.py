from uuid import uuid4
from django.db import models
from .application import Application

class Reference(models.Model):
    """
    Model for REFERENCE table
    """
    reference_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    reference = models.IntegerField(blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    years_known = models.IntegerField(blank=True)
    months_known = models.IntegerField(blank=True)
    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)

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
            'reference',
            'first_name',
            'last_name',
            'relationship',
            'years_known',
            'months_known',
            'street_line1',
            'street_line2',
            'town',
            'county',
            'country',
            'postcode',
            'phone_number',
            'email'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_address(self):
        return self.street_line1 + ', ' + self.street_line2 + ', ' + self.town + ', ' + self.postcode

    def get_time_known(self):
        months = self.months_known
        months_str = str(months) + ' months, ' if months != 1 else str(months) + ' month, '
        years = self.years_known
        years_str = str(years) + ' years' if years != 1 else str(years) + ' year'
        return months_str + years_str
    
    def get_ref_as_string(self):
        return 'First' if self.reference == 1 else 'Second'

    def get_summary_table(self):
        return [
            {"title": self.get_ref_as_string() + " reference", "id": self.pk},
            {"name": "Full name", "value": self.first_name + ' ' + self.last_name},
            {"name": "How they know you", "value": self.relationship},
            {"name": "Known for", "value": self.get_time_known()},
            {"name": "Address", "value": self.get_address()},
            {"name": "Phone number", "value": self.phone_number},
            {"name": "Email address", "value": self.email}

        ]

    class Meta:
        db_table = 'REFERENCE'
