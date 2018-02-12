from django.http import JsonResponse

from .models import ArcReview, Application

global application_id


def review_application(request, application_id):
    if len(Application.objects.filter(application_id=application_id)) == 1:
        application = Application.objects.get(application_id=application_id)
        #call return task-list review page
    else:
        return JsonResponse({"message": "fail"})
