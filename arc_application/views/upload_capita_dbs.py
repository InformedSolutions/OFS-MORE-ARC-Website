import csv
from datetime import datetime
import json

from arc_application.decorators import group_required
from arc_application.models import CapitaDBSFile
from arc_application.services import dbs_api
from arc_application.forms import UploadCapitaDBSForm

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import InternalError
from django.shortcuts import render


def __format_last_upload():
    try:
        capita_dbs_file = CapitaDBSFile.objects.get(id=1)
        return '%s (%s)' % (capita_dbs_file.filename, capita_dbs_file.date_uploaded.strftime('%d/%m/%Y'))

    except CapitaDBSFile.DoesNotExist:
        return 'File yet to be uploaded.'


def __update_last_upload(filename):
    date = datetime.now().date()
    queryset = CapitaDBSFile.objects.all()

    if queryset.exists():
        queryset.delete()

    CapitaDBSFile.objects.create(filename=filename, date_uploaded=date)
    return None


def __format_csv_data(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=('date_of_birth', 'certificate_number', 'certificate_information', 'date_of_issue'))
        next(reader)  # Skip header line of csv file.
        data = [row for row in reader]

    csvfile.close()
    return data


def __handle_file_upload(filename):
    data = __format_csv_data(filename=filename)

    response = dbs_api.batch_overwrite(data)

    if response.status_code == 201:
        return

    elif response.status_code == 400:
        response_text = json.loads(response.text)
        raise ValidationError(response_text)

    else:
        response_text = json.loads(response.text)
        raise InternalError('The DBS API returned a %i status code. Response text: %s' % response.status_code, response_text)


@login_required
@group_required(settings.ARC_GROUP)
def upload_capita_dbs(request):

    if request.method == 'GET':
        form = UploadCapitaDBSForm()

    elif request.method == 'POST':
        form = UploadCapitaDBSForm(request.POST)

        if form.is_valid():
            try:
                __handle_file_upload(request.POST['capita_list_file'])
                __update_last_upload(request.POST['capita_list_file'])
            except ValidationError:
                form.add_error('capita_list_file', 'There was an error with the file you tried to upload. Check the file and try again')
            except InternalError:
                form.add_error('capita_list_file', 'We couldn\'t upload your new list. Try again')

    context = {
        'form': form,
        'formatted_last_upload': __format_last_upload()
    }

    return render(request, template_name='upload-capita-dbs.html', context=context)
