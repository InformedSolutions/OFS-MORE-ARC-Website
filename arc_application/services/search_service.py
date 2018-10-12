import datetime
import re

from django.db.models import Q

from arc_application.models import Application, ApplicantName
from arc_application.services.db_gateways import NannyGatewayActions


class SearchService:

    @staticmethod
    def search(name: str, dob: str, home_postcode: str, care_location_postcode: str, reference: str,
               application_type: str) -> dict:
        """
        Exposed method to allow searching, given the following parameters:
        :param name: A string contained within the first_name OR last_name of an Applicant
        :param dob: A string contained within the DOB of an Applicant
        :param home_postcode: A string contained within the home address postcode field for an Applicant
        :param care_location_postcode: A string contained within the care address(es) postcode field(s) for an Applicant
        :param reference: A string contained within the Application's reference number, only existing if submitted.
        :param application_type: A string of 'Childminder', 'Nanny' or 'All' that determines what records to fetch.
        :return: A dictionary containing the ordered search results, prepared for displaying on the arc search view.
        """
        search_args = (name, dob, home_postcode, care_location_postcode, reference)

        # Search both Childminder and Nanny applications
        if application_type == 'All':
            search_results = SearchService._search_childminders_and_nannies(*search_args)

        # Search Childminder applications only
        elif application_type == 'Childminder':
            search_results = SearchService._search_childminders(*search_args)

        # Search Nanny applications only
        elif application_type == 'Nanny':
            search_results = SearchService._search_nannies(*search_args)

        else:
            raise ValueError('application_type was set to {0}, an unexpected value.')

        formatted_results = SearchService._format_search_results(search_results)
        ordered_results = SearchService._order_search_results(formatted_results)

        return ordered_results

    @staticmethod
    def _search_childminders_and_nannies(name, dob, home_postcode, care_location_postcode, reference):
        search_args = (name, dob, home_postcode, care_location_postcode, reference)

        cm_search_results = SearchService._search_childminders(*search_args)
        nanny_search_results = SearchService._search_nannies(*search_args)

        combined_results = SearchService.__combine_search_results(cm_search_results, nanny_search_results)

        return combined_results

    @staticmethod
    def _search_nannies(name, date_of_birth, home_postcode, care_location_postcode, application_reference):
        """
        Function for handling the searching of nanny applications.
        Gets nanny applications by use of the gateway_actions API by formulating a request (params) with the passed parameters.
        :return: API response record
        """
        nanny_actions = NannyGatewayActions()

        params_list = [('name', name),
                       ('date_of_birth', date_of_birth),
                       ('home_postcode', home_postcode),
                       ('care_location_postcode', care_location_postcode),
                       ('application_reference', application_reference)]
        params = {key: val for key, val in params_list if val}

        search_results_response = nanny_actions.list('arc-search', params=params)

        return search_results_response.record

    @staticmethod
    def _search_childminders(name, dob, home_postcode, care_location_postcode, reference):
        """
        Function for handling childminder searches.
        First generates a queryset containing the childminder search results, then converts those search results to a
         standard dictionary format.
        :return: List of dictionaries containing filtered results.
        """
        query = Q()

        if len(reference) > 0:
            query.add(Q(application_reference__icontains=reference), Q.AND)

        query.add(
            Q(
                Q(applicantname__first_name__icontains=name) |
                Q(applicantname__last_name__icontains=name)
            ), Q.AND
        )

        if len(dob) > 0:
            # Split DOB by non-alpha characters
            split_dob = re.split(r"[^0-9]", dob)

            if len(split_dob) == 1:
                # If only one DOB part has been supplied assume it could be day month or year

                # Create four digit year if 2 digit year supplied
                if len(split_dob[0]) == 2:
                    previous_century_year = str(19) + split_dob[0]
                    current_century_year = str(20) + split_dob[0]
                else:
                    # Otherwise allow longer values to be directly issued against query
                    previous_century_year = split_dob[0]
                    current_century_year = split_dob[0]

                query.add(
                    Q(
                        Q(applicantpersonaldetails__birth_day=int(split_dob[0])) |
                        Q(applicantpersonaldetails__birth_month=int(split_dob[0])) |
                        Q(applicantpersonaldetails__birth_year=int(previous_century_year)) |
                        Q(applicantpersonaldetails__birth_year=int(current_century_year))
                    ), Q.AND
                )

            if len(split_dob) == 2:
                # If two DOBs part have been supplied, again assume second part is either a month or a year

                # Create four digit year if 2 digit year supplied
                if len(split_dob[1]) == 2:
                    previous_century_year = str(19) + split_dob[1]
                    current_century_year = str(20) + split_dob[1]
                else:
                    # Otherwise allow longer values to be directly issued against query
                    previous_century_year = split_dob[1]
                    current_century_year = split_dob[1]

                query.add(
                    Q(
                        Q(applicantpersonaldetails__birth_day=int(split_dob[0])),
                        Q(applicantpersonaldetails__birth_month=int(split_dob[0])) |
                        Q(applicantpersonaldetails__birth_month=int(split_dob[1])) |
                        Q(applicantpersonaldetails__birth_year=int(previous_century_year)) |
                        Q(applicantpersonaldetails__birth_year=int(current_century_year))
                    ), Q.AND
                )

            if len(split_dob) == 3:

                # Create four digit year if 2 digit year supplied
                if len(split_dob[2]) == 2:
                    previous_century_year = str(19) + split_dob[2]
                    current_century_year = str(20) + split_dob[2]
                else:
                    # Otherwise allow longer values to be directly issued against query
                    previous_century_year = split_dob[2]
                    current_century_year = split_dob[2]

                query.add(
                    Q(
                        Q(applicantpersonaldetails__birth_day=int(split_dob[0])),
                        Q(applicantpersonaldetails__birth_month=int(split_dob[0])) |
                        Q(applicantpersonaldetails__birth_month=int(split_dob[1])) |
                        Q(applicantpersonaldetails__birth_year=int(previous_century_year)) |
                        Q(applicantpersonaldetails__birth_year=int(current_century_year))
                    ), Q.AND
                )

        address_query = Q()

        home_address_query = Q()
        home_address_query.add(
            Q(
                Q(applicanthomeaddress__childcare_address=False),
                Q(applicanthomeaddress__postcode__icontains=home_postcode)
            ), Q.AND
        )

        home_address_query.add(
            Q(applicanthomeaddress__postcode__icontains=home_postcode), Q.OR
        )

        childcare_address_query = Q()
        childcare_address_query.add(
            Q(
                Q(applicanthomeaddress__childcare_address=True),
                Q(applicanthomeaddress__postcode__icontains=care_location_postcode)
            ), Q.AND
        )

        address_query.add(home_address_query, Q.OR)
        address_query.add(childcare_address_query, Q.AND)

        query.add(address_query, Q.AND)

        search_results_queryset = Application.objects.filter(query)

        search_results_dict = SearchService.__queryset_to_search_dict(search_results_queryset)

        return search_results_dict

    @staticmethod
    def __queryset_to_search_dict(queryset):
        """
        Converts a Childminder queryset to the same response formatting as a nanny search result record.
        The returned dictionary contains the minimum amount of information required to generate the search table.
        Note: date_submitted and date_accessed are also formatted to strings inside this function.
        :param queryset:
        :return: A search_list (List of search dictionaries)
        """
        search_list = [
            {'application_id': query.application_id,
             'application_reference': query.application_reference,
             'application_type': 'Childminder',
             'applicant_name': SearchService.__cm_get_name(query.application_id),
             'date_submitted': query.date_submitted.strftime('%d/%m/%Y'),
             'date_accessed': query.date_updated.strftime('%d/%m/%Y'),
             'submission_type': query.application_status}
            for query in queryset]

        return search_list

    @staticmethod
    def __cm_get_name(app_id):
        """
        Gets the applicant's first_name and last_name.
        :param app_id: Applicant's id
        :return: String of first_name, last_name
        """
        if ApplicantName.objects.filter(application_id=app_id).exists():
            applicant_name_record = ApplicantName.objects.get(application_id=app_id)

            first_name = applicant_name_record.first_name
            last_name = applicant_name_record.last_name

            return "{0} {1}".format(first_name, last_name)
        else:
            return ""

    @staticmethod
    def __combine_search_results(search_list1, search_list2):
        """
        Combines two search_lists into a single list.
        :return:
        """
        combined_list = search_list1.copy()
        combined_list += search_list2

        return combined_list

    @staticmethod
    def _order_search_results(search_list):
        """
        Orders search_list by it's date_accessed field.
        The key used will also append all blank values (None or "") for date_accessed to the end of the ordered list.
        :param search_list:
        :return: A sorted search_list
        """
        return sorted(search_list,
                      key=SearchService._order_dict,
                      reverse=True)

    @staticmethod
    def _order_dict(search_dict):
        """
        Converts the passed search_dict's date_submitted parameter to a datetime for comparison.
        If the date_submitted is invalid, returns the minimum value date.
        :param search_dict: Formatted dictionary, expecting date_submitted to be in format DD/MM/YYYY (aka %d/%m/%Y)
        :return: Datetime
        """
        return datetime.datetime.strptime(search_dict['date_submitted'], '%d/%m/%Y') if search_dict['date_submitted'] else datetime.datetime.min

    @staticmethod
    def _format_search_results(search_list):
        """
        Converts search results (in the form of a list of relevant dictionaries) to a dictionary the same information in a displayable format.
        :param search_list: A list of dictionaries to be displayed.
        :return: A list of dictionaries (of equal length to search_list) with appended and formatted information.
        """
        formatted_search_results = [
            {'application_id': search_dict['application_id'],
             'application_reference': search_dict['application_reference'],
             'application_type': search_dict['application_type'],
             'applicant_name': search_dict['applicant_name'],
             'date_submitted': search_dict['date_submitted'],
             'date_accessed': search_dict['date_accessed'],
             'submission_type': SearchService.__format_submission_type(search_dict['submission_type']),
             'summary_link': '/arc/search-summary?id=' + str(search_dict['application_id']),
             'audit_link': '/arc/auditlog?id={0}&app_type={1}'.format(str(search_dict['application_id']),
                                                                      search_dict['application_type'])}
            for search_dict in search_list]

        return formatted_search_results

    @staticmethod
    def __format_submission_type(submission_type: str) -> str:
        """
        Converts a submission_type to a displayable label string.
        :param submission_type: String of application's status, e.g 'DRAFTING'.
        :return: String containing a relevant label.
        """
        if submission_type == 'DRAFTING':
            return 'Draft'
        elif submission_type == 'ACCEPTED':
            return 'Pending checks'
        elif submission_type == 'FURTHER_INFORMATION':
            return 'Returned'
        elif submission_type == 'SUBMITTED':
            return 'New'
        elif submission_type == 'ARC_REVIEW':
            return 'Assigned'
        else:
            return ''
