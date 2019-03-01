from django.views import View

from arc_application.views.childminder_views.arc_summary import cc_summary
from arc_application.views.nanny_views.nanny_search_summary import NannySearchSummary


class SearchRouter(View):
    """
    View to route Search Application Summaries
    """
    cc_summary_view = staticmethod(cc_summary)
    NannySearchSummary_view = staticmethod(NannySearchSummary.as_view())

    def dispatch(self, request, *args, **kwargs):
        app_type = request.GET.get('app_type')
        if app_type == 'Childminder':
            return self.cc_summary_view(request)
        elif app_type == 'Nanny':
            return self.NannySearchSummary_view(request, *args, **kwargs)
        else:
            return ValueError('app_type is {0} but should have been "Nanny" or "Childminder"'.format(app_type))
