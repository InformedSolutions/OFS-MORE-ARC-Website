import datetime
from uuid import uuid4
from django.db import models
from .application import Application


class AdultInHome(models.Model):
    """
    Model for ADULT_IN_HOME table
    """
    adult_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    adult = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_day = models.IntegerField(blank=True)
    birth_month = models.IntegerField(blank=True)
    birth_year = models.IntegerField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    dbs_certificate_number = models.CharField(max_length=50, blank=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    validated = models.BooleanField(default=False)
    current_treatment = models.NullBooleanField(null=True)
    serious_illness = models.NullBooleanField(null=True)
    known_to_council = models.NullBooleanField(null=True)
    reasons_known_to_council_health_check = models.TextField(default='', null=True)
    hospital_admission = models.NullBooleanField(null=True)
    health_check_status = models.CharField(max_length=50, default='To do')
    email_resent = models.IntegerField(default=0)
    email_resent_timestamp = models.DateTimeField(null=True, blank=True)
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
            'adult',
            'first_name',
            'middle_names',
            'last_name',
            'birth_day',
            'birth_month',
            'birth_year',
            'relationship',
            'email',
            'dbs_certificate_number',
            'health_check_status'
        )

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
        summary_table = [
            {"title": self.get_full_name(), "id": self.pk},
            {"name": "Health questions status", "value": self.health_check_status},
            {"name": "Name", "value": self.get_full_name()},
            {"name": "Date of birth", "value": date_of_birth},
            {"name": "Relationship", "value": self.relationship},
            {"name": "Email", "value": self.email},
            {"name": "Ofsted DBS", "value": ("Yes" if self.capita == True else "No")},
            {"name": "DBS certificate number", "value": self.dbs_certificate_number},
            {"name": "Lived abroad", "value": ("Yes" if self.lived_abroad == True else "No")},
            {"name": "Known to council", "value": ("Yes" if self.known_to_council == True else "No")},
        ]

        if self.known_to_council == True:
            summary_table.append({"name": "Tell us why", "value": self.reasons_known_to_council_health_check})

        from .childcare_type import ChildcareType

        if ChildcareType.objects.get(application_id=self.application_id).zero_to_five:
           summary_table.insert(-1, {"name": "British Military Base", "value": self.military_base})

        return summary_table

    # Date of birth property created to keep DRY
    @property
    def date_of_birth(self):
        return datetime(year=self.birth_year, month=self.birth_month, day=self.birth_day)

    class Meta:
        db_table = 'ADULT_IN_HOME'
