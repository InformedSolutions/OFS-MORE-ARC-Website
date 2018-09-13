from uuid import uuid4
from django.db import models
from .application import Application

class ChildcareType(models.Model):
    """
    Model for CHILDCARE_TYPE table
    """
    childcare_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    zero_to_five = models.BooleanField()
    five_to_eight = models.BooleanField()
    eight_plus = models.BooleanField()
    overnight_care = models.NullBooleanField()

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
            'zero_to_five',
            'five_to_eight',
            'eight_plus',
            'overnight_care'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_register_name(self):
        zero_to_five = self.zero_to_five
        five_to_eight = self.five_to_eight
        eight_plus = self.eight_plus
        register = ''
        if zero_to_five and five_to_eight and eight_plus:
            register = 'Early Years Register and Childcare Register (both parts)'
        if not zero_to_five and five_to_eight and eight_plus:
            register = 'Childcare Register (both parts)'
        if zero_to_five and not five_to_eight and not eight_plus:
            register = 'Early Years Register'
        if zero_to_five and five_to_eight and not eight_plus:
            register = 'Early Years Register and Childcare Register (compulsory part)'
        if zero_to_five and not five_to_eight and eight_plus:
            register = 'Early Years Register and Childcare Register (voluntary part)'
        if not zero_to_five and five_to_eight and not eight_plus:
            register = 'Childcare Register (compulsory part)'
        if not zero_to_five and not five_to_eight and eight_plus:
            register = 'Childcare Register (voluntary part)'
        return register

    def get_bool_as_string(self, bool_field):
        if bool_field:
            return 'Yes'
        else:
            return 'No'

    def get_summary_table(self):
        return [
            {"title": "Type of childcare", "id": self.pk},
            {"name": "Looking after 0 to 5 year olds?", "value": self.get_bool_as_string(self.zero_to_five)},
            {"name": "Looking after 5 to 7 year olds? ", "value": self.get_bool_as_string(self.five_to_eight)},
            {"name": "Looking after 8 year olds and older? ", "value": self.get_bool_as_string(self.eight_plus)},
            {"name": "Registers", "value": self.get_register_name()},
            {"name": "Looking after children overnight?", "value": self.get_bool_as_string(self.overnight_care)}
        ]

    class Meta:
        db_table = 'CHILDCARE_TYPE'
