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
    cautions_convictions = models.NullBooleanField(blank=True)
    lived_abroad = models.NullBooleanField(blank=True)
    military_base = models.NullBooleanField(blank=True)
    capita = models.NullBooleanField(blank=True)
    on_update = models.NullBooleanField(blank=True)

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
        summary_table_dict = [{"title": "Criminal record checks", "id": self.pk}]

        if self.lived_abroad is not None:
            summary_table_dict.append({"name": "Have you lived outside of the UK in the last 5 years?",
                                       "value": self.get_bool_as_string(self.lived_abroad)})

        if self.military_base is not None:
            summary_table_dict.append({"name": "Have you lived or worked on a British military base in the last 5 years?",
                                       "value": self.get_bool_as_string(self.military_base)})

        if self.capita is not None:
            summary_table_dict.append({"name": "Do you have an Ofsted DBS Check?",
                                       "value": self.get_bool_as_string(self.capita)})

        if self.on_update is not None:
            summary_table_dict.append({"name": "Are you on the DBS update service?",
             "value": self.get_bool_as_string(self.on_update)})

        if self.dbs_certificate_number is not None:
            summary_table_dict.append({"name": "DBS certificate number",
                                       "value": self.dbs_certificate_number})

        if self.cautions_convictions is not None:
            summary_table_dict.append({"name": "Do you have any criminal cautions or convictions?",
                                       "value": self.get_bool_as_string(self.cautions_convictions)})

        return summary_table_dict

    class Meta:
        db_table = 'CRIMINAL_RECORD_CHECK'
