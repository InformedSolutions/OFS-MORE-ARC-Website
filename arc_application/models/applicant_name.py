from datetime import date
from uuid import uuid4
from django.db import models
from .applicant_personal_details import ApplicantPersonalDetails
from .application import Application


class ApplicantName(models.Model):
    """
    Model for APPLICANT_NAME table
    """
    name_id = models.UUIDField(primary_key=True, default=uuid4)
    personal_detail_id = models.ForeignKey(ApplicantPersonalDetails, on_delete=models.CASCADE,
                                           db_column='personal_detail_id')
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE,
                                       db_column='application_id')
    current_name = models.BooleanField(blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    other_title = models.CharField(max_length=100, blank=True, null=True)

    # Current name fields
    start_day = models.IntegerField(blank=True, null=True)
    start_month = models.IntegerField(blank=True, null=True)
    start_year = models.IntegerField(blank=True, null=True)
    end_day = models.IntegerField(blank=True, null=True)
    end_month = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)

    @classmethod
    def get_id(cls, app_id):
        personal_detail_id = ApplicantPersonalDetails.get_id(app_id)
        return cls.objects.get(personal_detail_id=personal_detail_id)

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

        return ('first_name', 'last_name', 'middle_names',)

    @property
    def full_name(self):
        return self.first_name + ' ' + ((self.middle_names+' ') if self.middle_names else '') + self.last_name

    def get_summary_table(self):
        if self.title is not None:
            return [
                {"name": "Title",
                "value": self.title,
                'pk':self.pk, "index": 1
            },
                {"name": "Your name",
                "value": self.full_name,
                'pk': self.pk, "index": 1},
            ]
        else:
            return [ {"name": "Your name",
                "value": self.full_name,
                'pk': self.pk, "index": 1},
            ]

    class Meta:
        db_table = 'APPLICANT_NAME'

    def get_start_date(self):
        if not all((self.start_year, self.start_month, self.start_day)):
            return None
        return date(self.start_year, self.start_month, self.start_day)

    def set_start_date(self, start_date):
        self.start_year = start_date.year
        self.start_month = start_date.month
        self.start_day = start_date.day

    start_date = property(get_start_date, set_start_date)

    def get_end_date(self):
        if not all((self.end_year, self.end_month, self.end_day)):
            return None
        return date(self.end_year, self.end_month, self.end_day)

    def set_end_date(self, end_date):
        self.end_year = end_date.year
        self.end_month = end_date.month
        self.end_day = end_date.day

    end_date = property(get_end_date, set_end_date)
