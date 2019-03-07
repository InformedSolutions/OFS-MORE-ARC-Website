from uuid import uuid4
from django.db import models


class PreviousAddress(models.Model):
    """
    Model for PREVIOUS_ADDRESS table, used to contain previous
    """
    # Options for type discriminator
    previous_name_types = (
        ('ADULT', 'ADULT'),
        ('CHILD', 'CHILD'),
        ('APPLICANT', 'APPLICANT'),
    )

    # Primary key
    previous_name_id = models.UUIDField(primary_key=True, default=uuid4)

    # Foreign key for both adult and child in home
    person_id = models.UUIDField(blank=True)

    # Type discriminator
    person_type = models.CharField(choices=previous_name_types, max_length=50, blank=True)

    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=100, blank=True)


    class Meta:
        db_table = 'PREVIOUS_ADDRESS'
