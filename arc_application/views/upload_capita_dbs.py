from django.shortcuts import render


def upload_capita_dbs(request):
    return render(request, template_name='upload-capita-dbs.html')
