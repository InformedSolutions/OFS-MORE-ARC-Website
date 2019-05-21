from .nanny_childcare_address import NannyChildcareAddressSummary
from .nanny_childcare_training import NannyChildcareTrainingSummary
from .nanny_contact_details import NannyContactDetailsSummary
from .nanny_dbs_check import NannyDbsCheckSummary
from .nanny_first_aid import NannyFirstAidTrainingSummary
from .nanny_insurance_cover import NannyInsuranceCoverSummary
from .nanny_personal_details import NannyPersonalDetailsSummary


def get_nanny_summary_functions():
    """
    Function for returning function pointers to retrieving nanny context data
    """
    return [
        NannyContactDetailsSummary.create_context,
        NannyPersonalDetailsSummary().get_context_data,
        NannyChildcareAddressSummary().get_context_data,
        NannyFirstAidTrainingSummary().get_context_data,
        NannyChildcareTrainingSummary().get_context_data,
        NannyDbsCheckSummary().get_context_data,
        NannyInsuranceCoverSummary().get_context_data
    ]


def get_nanny_summary_variables(application_id):
    """
    Shared method for exporting Nanny application summary details
    :param application_id: the unique identifier of the application
    """
    context_function_list = get_nanny_summary_functions()
    context_list = [context_func(application_id) for context_func in context_function_list if context_func]

    # Remove 'Review: ' from page titles.
    # FIXME Change each view to use verbose_task_name property instead.
    for context in context_list:
        context['title'] = context['title'][7:]

    return context_list
