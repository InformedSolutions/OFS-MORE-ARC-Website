import csv
import logging
from datetime import datetime
import json

from ..decorators import group_required
from ..models import CapitaDBSFile
from ..services import dbs_api
from ..forms import UploadCapitaDBSForm

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import InternalError
from django.shortcuts import render

# Initiate logging
log = logging.getLogger()

def __format_last_upload():
    try:
        capita_dbs_file = CapitaDBSFile.objects.get(pk=1)
        return '%s (%s)' % (capita_dbs_file.filename, capita_dbs_file.date_uploaded.strftime('%d/%m/%Y'))

    except CapitaDBSFile.DoesNotExist:
        return 'File yet to be uploaded.'


def __update_last_upload(csv_file_name):
    date = datetime.now().date()

    try:
        capita_dbs_file = CapitaDBSFile.objects.get(pk=1)
        capita_dbs_file.filename = csv_file_name
        capita_dbs_file.date_uploaded = date
        capita_dbs_file.save()

    except CapitaDBSFile.DoesNotExist:
        CapitaDBSFile.objects.create(filename=csv_file_name, date_uploaded=date)

    return None


def __format_csv_data(csvfile):
    reader = csv.DictReader(csvfile, fieldnames=('date_of_birth', 'certificate_number', 'certificate_information', 'date_of_issue'))
    next(reader)  # Skip header line of csv file.
    data = [row for row in reader]

    return data


def __handle_file_upload(request_files):
    response = dbs_api.batch_overwrite({'capita_list_file': request_files['capita_list_file'].file})

    if response.status_code == 201:
        return

    elif response.status_code == 400:
        response_text = json.loads(response.text)
        raise ValidationError(response_text)

    else:

        try:
            response_text = json.loads(response.text)
        except json.JSONDecodeError:
            response_text = 'No response text to show.'

        raise InternalError('The DBS API returned a %i status code. Response text: %s' % (response.status_code, response_text))


@login_required
@group_required(settings.ARC_GROUP)
def upload_capita_dbs(request):

    if request.method == 'GET':
        form = UploadCapitaDBSForm()


    elif request.method == 'POST':
        form = UploadCapitaDBSForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                __handle_file_upload(request.FILES)
                __update_last_upload(request.FILES['capita_list_file'].name)
                log.debug("Handling submissions for upload DBS page - success")
            except ValidationError:
                form.add_error('capita_list_file', 'There was an error with the file you tried to upload. Check the file and try again')
            except InternalError:
                form.add_error('capita_list_file', 'We couldn\'t upload your new list. Try again')

    context = {
        'form': form,
        'formatted_last_upload': __format_last_upload()
    }
    log.debug("Rendering upload DBS page")
    return render(request, template_name='upload-capita-dbs.html', context=context)
