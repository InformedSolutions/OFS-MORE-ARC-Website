from uuid import uuid4
from django.db import models
from .application import Application

class CriminalRecordCheck(models.Model):
    """
    Model for CRIMINAL_RECORD_CHECK table
    """
    criminal_record_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    dbs_certificate_number = models.CharField(max_length=50, blank=True)
    cautions_convictions = models.BooleanField(blank=True)

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
            'dbs_certificate_number',
            'cautions_convictions'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_bool_as_string(self, bool_field):
        if bool_field:
            return 'Yes'
        else:
            return 'No'

    def get_summary_table(self):
        return [
            {"title": "Criminal record (DBS) check", "id": self.pk},
            {"name": "DBS certificate number", "value": self.dbs_certificate_number},
            {"name": "Do you have any criminal cautions or convictions?",
             "value": self.get_bool_as_string(self.cautions_convictions)}
        ]

    class Meta:
        db_table = 'CRIMINAL_RECORD_CHECK'
