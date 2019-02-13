import csv
import json

from arc_application.decorators import group_required
from arc_application.services import dbs_api
from arc_application.forms import UploadCapitaDBSForm

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def __format_last_upload():
    return None


def __handle_file_upload(f):

    if f.lower().endswith('.csv'):
        with open(f, 'r') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=('date_of_birth', 'certificate_number', 'certificate_information', 'date_of_issue'))

            next(reader)  # Skip first line of csv file.

            # data = json.dumps([row for row in reader])
            data = json.dumps([next(reader) for row in range(10)])
            print (data)


@login_required
@group_required(settings.ARC_GROUP)
def upload_capita_dbs(request):

    if request.method == 'GET':
        form = UploadCapitaDBSForm()

    elif request.method == 'POST':
        form = UploadCapitaDBSForm(request.POST)

        if form.is_valid():
            __handle_file_upload(request.POST['capita_list_file'])

    context = {
        'form': form,
        'formatted_last_upload': __format_last_upload()
    }

    return render(request, template_name='upload-capita-dbs.html', context=context)
