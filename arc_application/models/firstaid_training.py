from uuid import uuid4
from django.db import models
from .application import Application


class FirstAidTraining(models.Model):
    """
    Model for FIRST_AID_TRAINING table
    """
    first_aid_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    training_organisation = models.CharField(max_length=100)
    course_title = models.CharField(max_length=100)
    course_day = models.IntegerField()
    course_month = models.IntegerField()
    course_year = models.IntegerField()
    show_certificate = models.NullBooleanField(blank=True, null=True, default=None)
    renew_certificate = models.NullBooleanField(blank=True, null=True, default=None)

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
            'training_organisation',
            'course_title',
            'course_day',
            'course_month',
            'course_year',
            'show_certificate',
            'renew_certificate'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    def get_summary_table(self):

        if self.course_day < 10:
            course_day = '0' + str(self.course_day)
        else:
            course_day = str(self.course_day)

        if self.course_month < 10:
            course_month = '0' + str(self.course_month)
        else:
            course_month = str(self.course_month)

        return [
            {"title": "First aid training", "id": self.pk},
            {"name": "Training organisation", "value": self.training_organisation},
            {"name": "Title of training course", "value": self.course_title},
            {"name": "Date you completed course",
             "value": str(course_day) + '/' + str(course_month) + '/' + str(self.course_year)}
        ]

    class Meta:
        db_table = 'FIRST_AID_TRAINING'
