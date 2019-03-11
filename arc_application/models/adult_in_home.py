import datetime
from datetime import date
from uuid import uuid4

from django.db import models

from .application import Application
from .childcare_type import ChildcareType


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
    cygnum_relationship_to_childminder = models.CharField(max_length=100, blank=True)

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
    capita = models.NullBooleanField(blank=True)  # dbs was found on capita list?
    enhanced_check = models.NullBooleanField(blank=True)  # stated they have a capita dbs?
    on_update = models.NullBooleanField(blank=True)  # stated they are signed up to dbs update service?
    certificate_information = models.TextField(blank=True)  # information from dbs certificate
    within_three_months = models.NullBooleanField(blank=True)  # dbs was issued within three months of lookup?

    # Current name fields
    start_day = models.IntegerField(blank=True, null=True)
    start_month = models.IntegerField(blank=True, null=True)
    start_year = models.IntegerField(blank=True, null=True)
    end_day = models.IntegerField(blank=True, null=True)
    end_month = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)

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
            'health_check_status',
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

    @staticmethod
    def bool_to_string(bool):
        return "Yes" if bool else "No"

    def get_summary_table(self, apply_filtering_for_eyc=False):
        """
        Method for generating a summary table of details pertaining to an adult
        :param apply_filtering_for_eyc: a flag to indicate whether fields should be excluded when used to generate EYC
        summary tables
        :return: a summary table of the adult
        """

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
            {"title": self.get_full_name(),
             "id": self.pk},
            {"name": "Health questions status",
             "value": self.health_check_status},
            {"name": "Name",
             "value": self.get_full_name()},
            {"name": "Date of birth",
             "value": date_of_birth},
            {"name": "Relationship",
             "value": self.relationship},
            {"name": "Email",
             "value": self.email},
            {"name": "Lived abroad in the last 5 years?",
             "value": self.bool_to_string(self.lived_abroad)},
        ]

        if ChildcareType.objects.get(application_id=self.application_id).zero_to_five:
            summary_table += [
                {"name": "Lived or worked on British military base in the last 5 years?",
                 "value": self.bool_to_string(self.military_base)}
            ]

        summary_table += [
            {"name": "Did they get their DBS check from the Ofsted DBS application website?",
             "value": self.bool_to_string(self.capita)},
        ]

        if self.capita:
            summary_table += [
                {"name": "Is it dated within the last 3 months?",
                 "value": self.bool_to_string(self.within_three_months)}
            ]

        summary_table += [
            {"name": "DBS certificate number",
             "value": self.dbs_certificate_number},
        ]

        if self.show_enhanced_check():
            summary_table += [
                {"name": "Enhanced DBS check for home-based childcare?",
                 "value": self.bool_to_string(self.enhanced_check)}
            ]

        if self.show_on_update():
            summary_table += [
                {"name": "On the update service?",
                 "value": self.bool_to_string(self.on_update)}
            ]

        if not apply_filtering_for_eyc:
            summary_table += [
                {"name": "Known to council social Services in regards to their own children?",
                 "value": self.bool_to_string(self.known_to_council)},
            ]

            if self.known_to_council:
                summary_table += [
                    {"name": "Tell us why",
                     "value": self.reasons_known_to_council_health_check}
                ]

        return summary_table

    def show_enhanced_check(self):
        return not self.capita

    def show_on_update(self):
        return (not self.capita and self.enhanced_check) \
               or (self.capita and not self.within_three_months)

    # Date of birth property created to keep DRY
    @property
    def date_of_birth(self):
        return datetime(year=self.birth_year, month=self.birth_month, day=self.birth_day)

    class Meta:
        db_table = 'ADULT_IN_HOME'

    def get_start_date(self):
        return date(self.start_year, self.start_month, self.start_day)

    def set_start_date(self, start_date):
        self.start_year = start_date.year
        self.start_month = start_date.month
        self.start_day = start_date.day

    start_date = property(get_start_date, set_start_date)

    def get_end_date(self):
        return date(self.end_year, self.end_month, self.end_day)

    def set_end_date(self, end_date):
        self.end_year = end_date.year
        self.end_month = end_date.month
        self.end_day = end_date.day

    end_date = property(get_end_date, set_end_date)
