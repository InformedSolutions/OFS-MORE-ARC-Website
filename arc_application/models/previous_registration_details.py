from uuid import uuid4
from django.db import models
from .application import Application


class PreviousRegistrationDetails(models.Model):
    """
    Model for PREVIOUS_REGISTRATION_DETAILS table
    """
    previous_registration_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    previous_registration = models.BooleanField(default=False)
    individual_id = models.IntegerField(default=0, null=True, blank=True)
    five_years_in_UK = models.BooleanField(default=False)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_summary_table(self):
        return [
            {"title": "Individual lookup", "id": self.pk},
            {"name": "Individual Id", "value": self.individual_id if self.previous_registration else 'Not known to Ofsted'},
        ]

    class Meta:
        db_table = 'PREVIOUS_REGISTRATION_DETAILS'
