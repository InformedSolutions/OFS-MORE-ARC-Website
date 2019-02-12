from arc_application.services import dbs_api
from arc_application.forms import UploadCapitaDBSForm

from django.shortcuts import render


def __format_last_upload():
    return None


def __handle_file_upload(f):
    pass


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
