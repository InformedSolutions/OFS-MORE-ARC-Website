from uuid import uuid4
from django.db import models
from .application import Application
from datetime import date


class ApplicantPersonalDetails(models.Model):
    """
    Model for APPLICANT_PERSONAL_DETAILS table
    """
    personal_detail_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    birth_day = models.IntegerField(blank=True, null=True)
    birth_month = models.IntegerField(blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)

    # Date fields
    moved_in_day = models.IntegerField(blank=True, null=True)
    moved_in_month = models.IntegerField(blank=True, null=True)
    moved_in_year = models.IntegerField(blank=True, null=True)
    moved_out_day = models.IntegerField(blank=True, null=True)
    moved_out_month = models.IntegerField(blank=True, null=True)
    moved_out_year = models.IntegerField(blank=True, null=True)

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

        return ('birth_day', 'birth_month', 'birth_year',)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_summary_table(self):

        if self.birth_day < 10:
            birth_day = '0' + str(self.birth_day)
        else:
            birth_day = str(self.birth_day)

        if self.birth_month == 1:
            birth_month = 'Jan'
        elif self.birth_month == 2:
            birth_month = 'Feb'
        elif self.birth_month == 3:
            birth_month = 'Mar'
        elif self.birth_month == 4:
            birth_month = 'Apr'
        elif self.birth_month == 5:
            birth_month = 'May'
        elif self.birth_month == 6:
            birth_month = 'Jun'
        elif self.birth_month == 7:
            birth_month = 'Jul'
        elif self.birth_month == 8:
            birth_month = 'Aug'
        elif self.birth_month == 9:
            birth_month = 'Sep'
        elif self.birth_month == 10:
            birth_month = 'Oct'
        elif self.birth_month == 11:
            birth_month = 'Nov'
        elif self.birth_month == 12:
            birth_month = 'Dec'

        return [
                {"title": "Your name and date of birth", "id": self.personal_detail_id, "index": 0},
                {"name": "Date of birth",
                 "value": birth_day + ' ' + birth_month + ' ' + str(self.birth_year), 'pk': self.pk, "index": 2}
            ]

    class Meta:
        db_table = 'APPLICANT_PERSONAL_DETAILS'

    def get_moved_in_date(self):
        return date(self.moved_in_year, self.moved_in_month, self.moved_in_day)

    def set_moved_in_date(self, moved_in_date):
        self.moved_in_year = moved_in_date.year
        self.moved_in_month = moved_in_date.month
        self.moved_in_day = moved_in_date.day

    moved_in_date = property(get_moved_in_date, set_moved_in_date)

    def get_moved_out_date(self):
        return date(self.moved_out_year, self.moved_out_month, self.moved_out_day)

    def set_moved_out_date(self, moved_out_date):
        self.moved_out_year = moved_out_date.year
        self.moved_out_month = moved_out_date.month
        self.moved_out_day = moved_out_date.day

    moved_out_date = property(get_moved_out_date, set_moved_out_date)
