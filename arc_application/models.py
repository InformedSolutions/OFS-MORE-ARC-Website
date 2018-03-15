from __future__ import unicode_literals

from uuid import uuid4

from django.contrib.postgres.fields import JSONField
from django.db import models

TASK_STATUS = (
    ('NOT_STARTED', 'NOT_STARTED'),
    ('FLAGGED', 'FLAGGED'),
    ('COMPLETE', 'COMPLETE')
)


class AuditLog(models.Model):
    application_id = models.UUIDField(primary_key=True, default=uuid4)
    audit_message = JSONField(blank=True)

    class Meta:
        db_table = 'AUDIT_LOG'


class ArcComments(models.Model):
    review_id = models.UUIDField(primary_key=True, default=uuid4, unique=True),
    table_pk = models.UUIDField(blank=True)
    table_name = models.CharField(max_length=30, blank=True)
    field_name = models.CharField(max_length=30, blank=True)
    comment = models.CharField(max_length=100, blank=True)
    flagged = models.BooleanField()

    class Meta:
        db_table = 'ARC_COMMENTS'


class Arc(models.Model):
    application_id = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.CharField(max_length=50, blank=True)
    last_accessed = models.CharField(max_length=50)
    app_type = models.CharField(max_length=50)
    comments = models.CharField(blank=True, max_length=400)
    # What was previously ArcStatus is below
    login_details_review = models.CharField(choices=TASK_STATUS, max_length=50)
    childcare_type_review = models.CharField(choices=TASK_STATUS, max_length=50)
    personal_details_review = models.CharField(choices=TASK_STATUS, max_length=50)
    first_aid_review = models.CharField(choices=TASK_STATUS, max_length=50)
    dbs_review = models.CharField(choices=TASK_STATUS, max_length=50)
    health_review = models.CharField(choices=TASK_STATUS, max_length=50)
    references_review = models.CharField(choices=TASK_STATUS, max_length=50)
    people_in_home_review = models.CharField(choices=TASK_STATUS, max_length=50)

    class Meta:
        db_table = 'ARC'


class AdultInHome(models.Model):
    adult_id = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=100)
    middle_names = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_day = models.IntegerField()
    birth_month = models.IntegerField()
    birth_year = models.IntegerField()
    relationship = models.CharField(max_length=100)
    dbs_certificate_number = models.CharField(max_length=50)
    application = models.ForeignKey('Application', models.DO_NOTHING)
    adult = models.IntegerField(blank=True, null=True)
    permission_declare = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'ADULT_IN_HOME'


class ApplicantHomeAddress(models.Model):
    home_address_id = models.UUIDField(primary_key=True)
    street_line1 = models.CharField(max_length=100)
    street_line2 = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postcode = models.CharField(max_length=8)
    childcare_address = models.NullBooleanField()
    current_address = models.NullBooleanField()
    move_in_month = models.IntegerField()
    move_in_year = models.IntegerField()
    personal_detail = models.ForeignKey('ApplicantPersonalDetails', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'APPLICANT_HOME_ADDRESS'


class ApplicantName(models.Model):
    name_id = models.UUIDField(primary_key=True)
    current_name = models.BooleanField()
    first_name = models.CharField(max_length=100)
    middle_names = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    personal_detail = models.ForeignKey('ApplicantPersonalDetails', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'APPLICANT_NAME'


class ApplicantPersonalDetails(models.Model):
    personal_detail_id = models.UUIDField(primary_key=True)
    birth_day = models.IntegerField(blank=True, null=True)
    birth_month = models.IntegerField(blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)
    application = models.ForeignKey('Application', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'APPLICANT_PERSONAL_DETAILS'


class Application(models.Model):
    application_id = models.UUIDField(primary_key=True)
    application_type = models.CharField(max_length=50)
    application_status = models.CharField(max_length=50)
    cygnum_urn = models.CharField(max_length=50)
    login_details_status = models.CharField(max_length=50)
    personal_details_status = models.CharField(max_length=50)
    childcare_type_status = models.CharField(max_length=50)
    first_aid_training_status = models.CharField(max_length=50)
    eyfs_training_status = models.CharField(max_length=50)
    criminal_record_check_status = models.CharField(max_length=50)
    health_status = models.CharField(max_length=50)
    references_status = models.CharField(max_length=50)
    people_in_home_status = models.CharField(max_length=50)
    declarations_status = models.CharField(max_length=50)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    date_accepted = models.DateTimeField(blank=True, null=True)
    order_code = models.UUIDField(blank=True, null=True)
    login = models.ForeignKey('UserDetails', models.DO_NOTHING, blank=True, null=True)
    adults_in_home = models.NullBooleanField()
    children_in_home = models.NullBooleanField()
    children_turning_16 = models.NullBooleanField()
    background_check_declare = models.NullBooleanField()
    share_info_declare = models.NullBooleanField()
    inspect_home_declare = models.NullBooleanField()
    interview_declare = models.NullBooleanField()
    information_correct_declare = models.NullBooleanField()
    date_submitted = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'APPLICATION'


class ChildcareType(models.Model):
    childcare_id = models.UUIDField(primary_key=True)
    zero_to_five = models.BooleanField()
    five_to_eight = models.BooleanField()
    eight_plus = models.BooleanField()
    application = models.ForeignKey(Application, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CHILDCARE_TYPE'


class ChildInHome(models.Model):
    child_id = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=100)
    middle_names = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_day = models.IntegerField()
    birth_month = models.IntegerField()
    birth_year = models.IntegerField()
    relationship = models.CharField(max_length=100)
    application = models.ForeignKey(Application, models.DO_NOTHING)
    child = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CHILD_IN_HOME'


class CriminalRecordCheck(models.Model):
    criminal_record_id = models.UUIDField(primary_key=True)
    dbs_certificate_number = models.CharField(max_length=50)
    cautions_convictions = models.BooleanField()
    send_certificate_declare = models.NullBooleanField()
    application = models.ForeignKey(Application, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CRIMINAL_RECORD_CHECK'


class Eyfs(models.Model):
    eyfs_id = models.UUIDField(primary_key=True)
    eyfs_understand = models.NullBooleanField()
    eyfs_training_declare = models.NullBooleanField()
    share_info_declare = models.NullBooleanField()
    application = models.ForeignKey(Application, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'EYFS'


class FirstAidTraining(models.Model):
    first_aid_id = models.UUIDField(primary_key=True)
    training_organisation = models.CharField(max_length=100)
    course_title = models.CharField(max_length=100)
    course_day = models.IntegerField()
    course_month = models.IntegerField()
    course_year = models.IntegerField()
    application = models.ForeignKey(Application, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'FIRST_AID_TRAINING'


class Hdb(models.Model):
    hdb_id = models.UUIDField(primary_key=True)
    send_hdb_declare = models.NullBooleanField()
    application = models.ForeignKey(Application, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'HDB'


class Reference(models.Model):
    reference_id = models.UUIDField(primary_key=True)
    reference = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    years_known = models.IntegerField()
    months_known = models.IntegerField()
    street_line1 = models.CharField(max_length=100)
    street_line2 = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postcode = models.CharField(max_length=8)
    phone_number = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    application = models.ForeignKey(Application, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'REFERENCE'


class UserDetails(models.Model):
    login_id = models.UUIDField(primary_key=True)
    email = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)
    add_phone_number = models.CharField(max_length=20)
    email_expiry_date = models.IntegerField(blank=True, null=True)
    sms_expiry_date = models.IntegerField(blank=True, null=True)
    magic_link_email = models.CharField(max_length=100, blank=True, null=True)
    magic_link_sms = models.CharField(max_length=100, blank=True, null=True)
    security_question = models.CharField(max_length=100, blank=True, null=True)
    security_answer = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'USER_DETAILS'


class HealthDeclarationBooklet(models.Model):
    """
    Model for HEALTH_DECLARATION_BOOKLET table
    """
    hdb_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    send_hdb_declare = models.NullBooleanField(blank=True)

    class Meta:
        managed = False
        db_table = 'HDB'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class GovukTemplateBaseLink(models.Model):
    modified = models.DateTimeField()
    name = models.CharField(max_length=255)
    localise_name = models.BooleanField()
    link = models.CharField(max_length=255)
    link_is_view_name = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'govuk_template_base_link'


class GovukTemplateBaseServicesettings(models.Model):
    modified = models.DateTimeField()
    name = models.CharField(max_length=100)
    localise_name = models.BooleanField()
    phase = models.CharField(max_length=10)
    header_link_view_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'govuk_template_base_servicesettings'


class GovukTemplateBaseServicesettingsFooterLinks(models.Model):
    servicesettings = models.ForeignKey(GovukTemplateBaseServicesettings, models.DO_NOTHING)
    link = models.ForeignKey(GovukTemplateBaseLink, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'govuk_template_base_servicesettings_footer_links'
        unique_together = (('servicesettings', 'link'),)


class GovukTemplateBaseServicesettingsHeaderLinks(models.Model):
    servicesettings = models.ForeignKey(GovukTemplateBaseServicesettings, models.DO_NOTHING)
    link = models.ForeignKey(GovukTemplateBaseLink, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'govuk_template_base_servicesettings_header_links'
        unique_together = (('servicesettings', 'link'),)
