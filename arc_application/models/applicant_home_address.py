from uuid import uuid4
from django.db import models
from .applicant_personal_details import ApplicantPersonalDetails
from .application import Application


class ApplicantHomeAddress(models.Model):
    """
    Model for APPLICANT_HOME_ADDRESS table
    """
    home_address_id = models.UUIDField(primary_key=True, default=uuid4)
    personal_detail_id = models.ForeignKey(ApplicantPersonalDetails, on_delete=models.CASCADE,
                                           db_column='personal_detail_id')
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE,
                                       db_column='application_id')
    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8, blank=True)
    childcare_address = models.NullBooleanField(blank=True, null=True, default=None)
    current_address = models.NullBooleanField(blank=True, null=True, default=None)
    move_in_month = models.IntegerField(blank=True)
    move_in_year = models.IntegerField(blank=True)

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
            'street_line1',
            'street_line2',
            'town',
            'county',
            'country',
            'postcode',
            'childcare_address',
            'current_address',
            'move_in_month',
            'move_in_year'
        )

    @classmethod
    def get_id(cls, app_id):
        personal_detail_id = ApplicantPersonalDetails.get_id(app_id)
        return cls.objects.get(personal_detail_id=personal_detail_id)

    def get_bool_as_string(self, bool_field):
        if bool_field:
            return 'Yes'
        else:
            return 'No'

    def get_address(self):
        return self.street_line1 + ', ' + self.street_line2 + ', ' + self.town + ', ' + self.postcode

    def get_summary_table(self):
        array = []
        # If the home address is the same as the childcare address
        working_in_other_childminder_home = Application.objects.get(
            application_id=self.application_id_id).working_in_other_childminder_home
        own_children = Application.objects.get(application_id=self.application_id_id).own_children
        if self.current_address and self.childcare_address:
            home_address = self.get_address()
            childcare_address = 'Same as home address'
            return [
                {"name": "Your home address", "value": home_address, 'pk': self.pk, "index": 3},
                {"name": "Childcare address", "value": childcare_address, 'pk': self.pk, "index": 4},
                {"name": "Is this another childminder's home?",
                 "value": self.get_bool_as_string(working_in_other_childminder_home),
                 'pk': self.application_id_id, "index": 5},
                {"name": "Do you have children of your own under 16?", "value": self.get_bool_as_string(own_children),
                 'pk': self.application_id_id, "index": 6}
            ]
        # If the address is only a home address
        if self.current_address and not self.childcare_address:
            home_address = self.get_address()
            return [
                {"name": "Your home address", "value": home_address, 'pk': self.pk, "index": 3}
            ]
        # If the address is only a childcare address
        if not self.current_address and self.childcare_address:
            childcare_address = self.get_address()
            return [
                {"name": "Childcare address", "value": childcare_address, 'pk': self.pk, "index": 4},
                {"name": "Is this another childminder's home?",
                 "value": self.get_bool_as_string(working_in_other_childminder_home), 'pk': self.application_id_id,
                 "index": 5},
                {"name": "Do you have children of your own under 16?", "value": self.get_bool_as_string(own_children),
                 'pk': self.application_id_id, "index": 6}
            ]

    class Meta:
        db_table = 'APPLICANT_HOME_ADDRESS'
        app_label = 'application'
