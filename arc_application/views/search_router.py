from django.views import View

from ..views.childminder_views.arc_summary import cc_summary
from ..views.nanny_views.nanny_search_summary import NannySearchSummary
from ..views.adult_update_views.adult_update_search_summary import AdultUpdateSearchSummary


class SearchRouter(View):
    """
    View to route Search Application Summaries
    """
    cc_summary_view = staticmethod(cc_summary)
    NannySearchSummary_view = staticmethod(NannySearchSummary.as_view())
    AdultUpdateSearchSummary_view = staticmethod(AdultUpdateSearchSummary.as_view())

    def dispatch(self, request, *args, **kwargs):
        app_type = request.GET.get('app_type')
        if app_type == 'Childminder':
            return self.cc_summary_view(request)
        elif app_type == 'Nanny':
            return self.NannySearchSummary_view(request, *args, **kwargs)
        elif app_type == 'New Association':
            return self.AdultUpdateSearchSummary_view(request, *args, **kwargs)
        else:
            return ValueError('app_type is {0} but should have been "Nanny" or "Childminder"'.format(app_type))
