from uuid import uuid4
from django.db import models
from .application import Application
from .childcare_type import ChildcareType


class ChildcareTraining(models.Model):
    """
    Model for ChildcareTraining table
    """
    eyfs_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    eyfs_course_name = models.CharField(max_length=50, blank=True, )
    eyfs_course_date_day = models.IntegerField(blank=True, null=True)
    eyfs_course_date_month = models.IntegerField(blank=True, null=True)
    eyfs_course_date_year = models.IntegerField(blank=True, null=True)

    # Childcare Training for Childcare Register only applicants.

    eyfs_training = models.NullBooleanField(blank=True, null=True, default=None)
    common_core_training = models.NullBooleanField(blank=True, null=True, default=None)
    no_training = models.NullBooleanField(blank=True, null=True, default=None)

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
            'eyfs_course_name',
            'eyfs_course_date_day',
            'eyfs_course_date_month',
            'eyfs_course_date_year',
            'eyfs_training',
            'common_core_training',
            'no_training'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_summary_table(self):
        childcare_register_only = not ChildcareType.objects.get(application_id=self.application_id).zero_to_five

        # If the applicant applied for the EYFS register, return EYFS training details.
        # If they're applying to the Childcare Register only, return type of training course.
        if childcare_register_only:

            eyfs_training = self.eyfs_training
            common_core_training = self.common_core_training
            if eyfs_training and common_core_training:
                value = 'Training that covers the EYFS and training in common core skills'
            elif eyfs_training:
                value = 'Training that covers the EYFS'
            else:
                value = 'Training in common core skills'

            return [
                {"title": "Childcare training", "id": self.pk},
                {"name": "What type of childcare training have you completed?", "value": value},
            ]

        else:

            return [
                {"title": "Childcare training", "id": self.pk},
                {"name": "Title of training course", "value": self.eyfs_course_name},
                {"name": "Date you completed course",
                 "value": str(self.eyfs_course_date_day) + '/' + str(self.eyfs_course_date_month) + '/' + str(
                     self.eyfs_course_date_year)}
            ]

    class Meta:
        db_table = 'CHILDCARE_TRAINING'
