# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-01 10:05
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdultInHome',
            fields=[
                ('adult_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('adult', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('middle_names', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('birth_day', models.IntegerField(blank=True)),
                ('birth_month', models.IntegerField(blank=True)),
                ('birth_year', models.IntegerField(blank=True)),
                ('relationship', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('dbs_certificate_number', models.CharField(blank=True, max_length=50)),
                ('token', models.CharField(blank=True, max_length=100, null=True)),
                ('validated', models.BooleanField(default=False)),
                ('current_treatment', models.NullBooleanField()),
                ('serious_illness', models.NullBooleanField()),
                ('hospital_admission', models.NullBooleanField()),
                ('health_check_status', models.CharField(default='To do', max_length=50)),
                ('email_resent', models.IntegerField(default=0)),
                ('email_resent_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ADULT_IN_HOME',
            },
        ),
        migrations.CreateModel(
            name='ApplicantHomeAddress',
            fields=[
                ('home_address_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('street_line1', models.CharField(blank=True, max_length=100)),
                ('street_line2', models.CharField(blank=True, max_length=100)),
                ('town', models.CharField(blank=True, max_length=100)),
                ('county', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postcode', models.CharField(blank=True, max_length=8)),
                ('childcare_address', models.NullBooleanField(default=None)),
                ('current_address', models.NullBooleanField(default=None)),
                ('move_in_month', models.IntegerField(blank=True)),
                ('move_in_year', models.IntegerField(blank=True)),
            ],
            options={
                'db_table': 'APPLICANT_HOME_ADDRESS',
            },
        ),
        migrations.CreateModel(
            name='ApplicantName',
            fields=[
                ('name_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('current_name', models.BooleanField()),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('middle_names', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'db_table': 'APPLICANT_NAME',
            },
        ),
        migrations.CreateModel(
            name='ApplicantPersonalDetails',
            fields=[
                ('personal_detail_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('birth_day', models.IntegerField(blank=True, null=True)),
                ('birth_month', models.IntegerField(blank=True, null=True)),
                ('birth_year', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'APPLICANT_PERSONAL_DETAILS',
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('application_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('application_type', models.CharField(blank=True, choices=[('CHILDMINDER', 'CHILDMINDER'), ('NANNY', 'NANNY'), ('NURSERY', 'NURSERY'), ('SOCIAL_CARE', 'SOCIAL_CARE')], max_length=50)),
                ('application_status', models.CharField(blank=True, choices=[('ARC_REVIEW', 'ARC_REVIEW'), ('CANCELLED', 'CANCELLED'), ('CYGNUM_REVIEW', 'CYGNUM_REVIEW'), ('DRAFTING', 'DRAFTING'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION'), ('NOT_REGISTERED', 'NOT_REGISTERED'), ('REGISTERED', 'REGISTERED'), ('REJECTED', 'REJECTED'), ('SUBMITTED', 'SUBMITTED'), ('WITHDRAWN', 'WITHDRAWN')], max_length=50)),
                ('cygnum_urn', models.CharField(blank=True, max_length=50)),
                ('login_details_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('login_details_arc_flagged', models.BooleanField(default=False)),
                ('personal_details_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('personal_details_arc_flagged', models.BooleanField(default=False)),
                ('childcare_type_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('childcare_type_arc_flagged', models.BooleanField(default=False)),
                ('first_aid_training_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('first_aid_training_arc_flagged', models.BooleanField(default=False)),
                ('eyfs_training_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('eyfs_training_arc_flagged', models.BooleanField(default=False)),
                ('criminal_record_check_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('criminal_record_check_arc_flagged', models.BooleanField(default=False)),
                ('health_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('health_arc_flagged', models.BooleanField(default=False)),
                ('references_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('references_arc_flagged', models.BooleanField(default=False)),
                ('people_in_home_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('people_in_home_arc_flagged', models.BooleanField(default=False)),
                ('adults_in_home', models.NullBooleanField(default=None)),
                ('children_in_home', models.NullBooleanField(default=None)),
                ('children_turning_16', models.NullBooleanField(default=None)),
                ('declarations_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FLAGGED', 'FLAGGED')], max_length=50)),
                ('share_info_declare', models.NullBooleanField(default=None)),
                ('display_contact_details_on_web', models.NullBooleanField(default=None)),
                ('suitable_declare', models.NullBooleanField(default=None)),
                ('information_correct_declare', models.NullBooleanField(default=None)),
                ('change_declare', models.NullBooleanField(default=None)),
                ('date_created', models.DateTimeField(blank=True, null=True)),
                ('date_updated', models.DateTimeField(blank=True, null=True)),
                ('date_accepted', models.DateTimeField(blank=True, null=True)),
                ('date_submitted', models.DateTimeField(blank=True, null=True)),
                ('application_reference', models.CharField(blank=True, max_length=9, null=True, validators=[django.core.validators.RegexValidator('(\\w{2})([0-9]{7})')])),
                ('ofsted_visit_email_sent', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'APPLICATION',
            },
        ),
        migrations.CreateModel(
            name='ApplicationReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.IntegerField(validators=[django.core.validators.MaxValueValidator(9999999)])),
            ],
            options={
                'db_table': 'APPLICATION_REFERENCE',
            },
        ),
        migrations.CreateModel(
            name='Arc',
            fields=[
                ('application_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('user_id', models.CharField(blank=True, max_length=50)),
                ('last_accessed', models.CharField(max_length=50)),
                ('app_type', models.CharField(max_length=50)),
                ('login_details_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('childcare_type_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('personal_details_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('first_aid_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('eyfs_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('dbs_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('health_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('references_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('people_in_home_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('childcare_address_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('childcare_training_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
                ('insurance_cover_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50)),
            ],
            options={
                'db_table': 'ARC',
            },
        ),
        migrations.CreateModel(
            name='ArcComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_pk', models.UUIDField(blank=True)),
                ('table_name', models.CharField(blank=True, max_length=30)),
                ('field_name', models.CharField(blank=True, max_length=40)),
                ('comment', models.CharField(blank=True, max_length=100)),
                ('flagged', models.BooleanField()),
            ],
            options={
                'db_table': 'ARC_COMMENTS',
            },
        ),
        migrations.CreateModel(
            name='ChildcareType',
            fields=[
                ('childcare_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('zero_to_five', models.BooleanField()),
                ('five_to_eight', models.BooleanField()),
                ('eight_plus', models.BooleanField()),
                ('overnight_care', models.NullBooleanField()),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'CHILDCARE_TYPE',
            },
        ),
        migrations.CreateModel(
            name='ChildInHome',
            fields=[
                ('child_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('child', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('middle_names', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('birth_day', models.IntegerField(blank=True)),
                ('birth_month', models.IntegerField(blank=True)),
                ('birth_year', models.IntegerField(blank=True)),
                ('relationship', models.CharField(blank=True, max_length=100)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'CHILD_IN_HOME',
            },
        ),
        migrations.CreateModel(
            name='CriminalRecordCheck',
            fields=[
                ('criminal_record_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('dbs_certificate_number', models.CharField(blank=True, max_length=50)),
                ('cautions_convictions', models.BooleanField()),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'CRIMINAL_RECORD_CHECK',
            },
        ),
        migrations.CreateModel(
            name='EYFS',
            fields=[
                ('eyfs_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('eyfs_course_name', models.CharField(blank=True, max_length=50)),
                ('eyfs_course_date_day', models.IntegerField(blank=True, null=True)),
                ('eyfs_course_date_month', models.IntegerField(blank=True, null=True)),
                ('eyfs_course_date_year', models.IntegerField(blank=True, null=True)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'EYFS',
            },
        ),
        migrations.CreateModel(
            name='FirstAidTraining',
            fields=[
                ('first_aid_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('training_organisation', models.CharField(max_length=100)),
                ('course_title', models.CharField(max_length=100)),
                ('course_day', models.IntegerField()),
                ('course_month', models.IntegerField()),
                ('course_year', models.IntegerField()),
                ('show_certificate', models.NullBooleanField(default=None)),
                ('renew_certificate', models.NullBooleanField(default=None)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'FIRST_AID_TRAINING',
            },
        ),
        migrations.CreateModel(
            name='HealthCheckCurrent',
            fields=[
                ('illness_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=150)),
                ('person_id', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='arc_application.AdultInHome')),
            ],
            options={
                'db_table': 'CURRENT_ILLNESS',
            },
        ),
        migrations.CreateModel(
            name='HealthCheckHospital',
            fields=[
                ('illness_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=150)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('person_id', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='arc_application.AdultInHome')),
            ],
            options={
                'db_table': 'HOSPITAL_ADMISSION',
                'ordering': ['start_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HealthCheckSerious',
            fields=[
                ('illness_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=150)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('person_id', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='arc_application.AdultInHome')),
            ],
            options={
                'db_table': 'SERIOUS_ILLNESS',
                'ordering': ['start_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HealthDeclarationBooklet',
            fields=[
                ('hdb_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('send_hdb_declare', models.NullBooleanField()),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'HDB',
            },
        ),
        migrations.CreateModel(
            name='OtherPersonPreviousRegistrationDetails',
            fields=[
                ('previous_registration_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('previous_registration', models.BooleanField(default=False)),
                ('individual_id', models.IntegerField(blank=True, default=0, null=True)),
                ('five_years_in_UK', models.BooleanField(default=False)),
                ('person_id', models.ForeignKey(db_column='person_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.AdultInHome')),
            ],
            options={
                'db_table': 'OTHER_PERSON_PREVIOUS_REGISTRATION_DETAILS',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('payment_reference', models.CharField(max_length=29)),
                ('payment_submitted', models.BooleanField(default=False)),
                ('payment_authorised', models.BooleanField(default=False)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'PAYMENT',
            },
        ),
        migrations.CreateModel(
            name='PreviousAddress',
            fields=[
                ('previous_name_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('person_id', models.UUIDField(blank=True)),
                ('person_type', models.CharField(blank=True, choices=[('ADULT', 'ADULT'), ('CHILD', 'CHILD'), ('APPLICANT', 'APPLICANT')], max_length=50)),
                ('street_line1', models.CharField(blank=True, max_length=100)),
                ('street_line2', models.CharField(blank=True, max_length=100)),
                ('town', models.CharField(blank=True, max_length=100)),
                ('county', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postcode', models.CharField(blank=True, max_length=8)),
            ],
            options={
                'db_table': 'PREVIOUS_ADDRESS',
            },
        ),
        migrations.CreateModel(
            name='PreviousName',
            fields=[
                ('previous_name_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('person_id', models.UUIDField(blank=True)),
                ('other_person_type', models.CharField(blank=True, choices=[('ADULT', 'ADULT'), ('CHILD', 'CHILD'), ('APPLICANT', 'APPLICANT')], max_length=200)),
                ('first_name', models.CharField(blank=True, max_length=200)),
                ('middle_names', models.CharField(blank=True, max_length=200)),
                ('last_name', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'db_table': 'PREVIOUS_NAME',
            },
        ),
        migrations.CreateModel(
            name='PreviousRegistrationDetails',
            fields=[
                ('previous_registration_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('previous_registration', models.BooleanField(default=False)),
                ('individual_id', models.IntegerField(blank=True, default=0, null=True)),
                ('five_years_in_UK', models.BooleanField(default=False)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'PREVIOUS_REGISTRATION_DETAILS',
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('reference_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('reference', models.IntegerField(blank=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('relationship', models.CharField(blank=True, max_length=100)),
                ('years_known', models.IntegerField(blank=True)),
                ('months_known', models.IntegerField(blank=True)),
                ('street_line1', models.CharField(blank=True, max_length=100)),
                ('street_line2', models.CharField(blank=True, max_length=100)),
                ('town', models.CharField(blank=True, max_length=100)),
                ('county', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postcode', models.CharField(blank=True, max_length=8)),
                ('phone_number', models.CharField(blank=True, max_length=50)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'REFERENCE',
                'ordering': ['reference'],
            },
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('login_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('mobile_number', models.CharField(blank=True, max_length=20)),
                ('add_phone_number', models.CharField(blank=True, max_length=20)),
                ('email_expiry_date', models.IntegerField(blank=True, null=True)),
                ('sms_expiry_date', models.IntegerField(blank=True, null=True)),
                ('magic_link_email', models.CharField(blank=True, max_length=100, null=True)),
                ('magic_link_sms', models.CharField(blank=True, max_length=100, null=True)),
                ('sms_resend_attempts', models.IntegerField(blank=True, default=0, null=True)),
                ('sms_resend_attempts_expiry_date', models.IntegerField(blank=True, default=0, null=True)),
                ('application_id', models.ForeignKey(db_column='application_id', default=uuid.uuid4, on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application')),
            ],
            options={
                'db_table': 'USER_DETAILS',
            },
        ),
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application'),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application'),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='personal_detail_id',
            field=models.ForeignKey(db_column='personal_detail_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.ApplicantPersonalDetails'),
        ),
        migrations.AddField(
            model_name='applicanthomeaddress',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application'),
        ),
        migrations.AddField(
            model_name='applicanthomeaddress',
            name='personal_detail_id',
            field=models.ForeignKey(db_column='personal_detail_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.ApplicantPersonalDetails'),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='arc_application.Application'),
        ),
    ]
