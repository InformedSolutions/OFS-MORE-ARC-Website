"""
Tests for assuring that SearchService is functioning correctly.
"""
from unittest.mock import patch

from django.test import TestCase, tag

from ...services.search_service import SearchService


class SearchServiceUnitTests(TestCase):
    """
    Test case for Nanny search tests.
    """

    @tag('unit')
    @patch('arc_application.services.search_service.SearchService._search_childminders')
    def test_search_only_childminder(self, mock_search_childminders):
        """
        Test to see if Childminder is being searched with 'Childminder' application_type.
        :param mock_search_childminders: Mock for _search_childminders method in SearchService.
        """
        SearchService.search("", "", "", "", "", 'Childminder')

        self.assertTrue(mock_search_childminders.call_count == 1)

    @tag('unit')
    @patch('arc_application.services.search_service.SearchService._search_nannies')
    def test_search_only_nannies(self, mock_search_nannies):
        """
        Test to see if Nanny is being searched with 'Nanny' application_type.
        :param mock_search_childminders: Mock for _search_childminders method in SearchService.
        """
        SearchService.search("", "", "", "", "", 'Nanny')

        self.assertTrue(mock_search_nannies.call_count == 1)

    @tag('unit')
    @patch('arc_application.services.search_service.SearchService._search_nannies')
    @patch('arc_application.services.search_service.SearchService._search_childminders')
    @patch('arc_application.services.search_service.SearchService._search_new_associations')
    def test_search_all(self, mock_search_childminders, mock_search_nannies, mock_search_new_associations):
        """
        Test to see if Childminder is being searched with 'All' application_type.
        :param mock_search_childminders: Mock for _search_childminders method in SearchService.
        :param mock_search_nannies: Mock for _search_nannies method in SearchService.
        """
        SearchService.search("", "", "", "", "", 'All')

        self.assertTrue(mock_search_childminders.call_count == 1)
        self.assertTrue(mock_search_nannies.call_count == 1)
        self.assertTrue(mock_search_new_associations.call_count == 1)

    @tag('unit')
    def test_ordering(self):
        """
        Test to see if ordering of search_dicts working as expected.
        """
        mock_search_dict_1 = {
            'audit_link': '/arc/auditlog?id=4c004204-84e1-4f47-b118-c91fbb47a0bf&app_type=Nanny',
            'summary_link': '/arc/search-summary?id=4c004204-84e1-4f47-b118-c91fbb47a0bf',
            'submission_type': 'Draft',
            'date_submitted': '03/06/2017',
            'application_type': 'Nanny',
            'application_reference': None,
            'applicant_name': '',
            'date_accessed': '',
            'application_id': '4c004204-84e1-4f47-b118-c91fbb47a0bf'
        }
        mock_search_dict_2 = {
            'audit_link': '/arc/auditlog?id=4c004204-84e1-4f47-b118-c91fbb47a0bf&app_type=Childminder',
            'summary_link': '/arc/search-summary?id=4c004204-84e1-4f47-b118-c91fbb47a0bf',
            'submission_type': 'Draft',
            'date_submitted': '',
            'application_type': 'Childminder',
            'application_reference': None,
            'applicant_name': '',
            'date_accessed': '',
            'application_id': '4c004204-84e1-4f47-b118-c91fbb47a0bf'
        }
        mock_search_dict_3 = {
            'audit_link': '/arc/auditlog?id=4c004204-84e1-4f47-b118-c91fbb47a0bf&app_type=Nanny',
            'summary_link': '/arc/search-summary?id=4c004204-84e1-4f47-b118-c91fbb47a0bf',
            'submission_type': 'Draft',
            'date_submitted': '05/04/2018',
            'application_type': 'Nanny',
            'application_reference': None,
            'applicant_name': '',
            'date_accessed': '',
            'application_id': '4c004204-84e1-4f47-b118-c91fbb47a0bf'
        }
        mock_search_dict_4 = {
            'audit_link': '/arc/auditlog?id=4c004204-84e1-4f47-b118-c91fbb47a0bf&app_type=Nanny',
            'summary_link': '/arc/search-summary?id=4c004204-84e1-4f47-b118-c91fbb47a0bf',
            'submission_type': 'Draft',
            'date_submitted': '09/04/2018',
            'application_type': 'Nanny',
            'application_reference': None,
            'applicant_name': '',
            'date_accessed': '',
            'application_id': '4c004204-84e1-4f47-b118-c91fbb47a0bf'
        }
        mock_search_dict_5 = {
            'audit_link': '/arc/auditlog?id=4c004204-84e1-4f47-b118-c91fbb47a0bf&app_type=Childminder',
            'summary_link': '/arc/search-summary?id=4c004204-84e1-4f47-b118-c91fbb47a0bf',
            'submission_type': 'Draft',
            'date_submitted': '10/10/2018',
            'application_type': 'Childminder',
            'application_reference': None,
            'applicant_name': '',
            'date_accessed': '',
            'application_id': '4c004204-84e1-4f47-b118-c91fbb47a0bf'
        }
        expected_order_list = [mock_search_dict_5, mock_search_dict_4, mock_search_dict_3, mock_search_dict_1,
                               mock_search_dict_2]
        mock_search_list = [mock_search_dict_1, mock_search_dict_2, mock_search_dict_3, mock_search_dict_4,
                            mock_search_dict_5]
        mock_search_list_reverse = [mock_search_dict_5, mock_search_dict_4, mock_search_dict_3, mock_search_dict_2,
                                    mock_search_dict_1]

        ordered_mock_search_list = SearchService._order_search_results(mock_search_list)
        ordered_mock_search_list_reverse = SearchService._order_search_results(mock_search_list_reverse)

        self.assertEqual(ordered_mock_search_list, expected_order_list)
        self.assertEqual(ordered_mock_search_list_reverse, expected_order_list)

    @tag('unit')
    def test_formatting(self):
        """
        Test to see if formatting of search_lists working as expected.
        """
        mock_search_list = [{
            'submission_type': 'ACCEPTED',
            'date_submitted': '03/06/2017',
            'application_type': 'Nanny',
            'application_reference': None,
            'applicant_name': 'Test Testington',
            'date_accessed': '',
            'application_id': '4c004204-84e1-4f47-b118-c91fbb47a0bf'
        }]

        expected_formatted_search_list = [{
            'audit_link': '/arc/auditlog?id=4c004204-84e1-4f47-b118-c91fbb47a0bf&app_type=Nanny',
            'summary_link': '/arc/search-summary?id=4c004204-84e1-4f47-b118-c91fbb47a0bf&app_type=Nanny',
            'submission_type': 'Pending checks',
            'date_submitted': '03/06/2017',
            'application_type': 'Nanny',
            'application_reference': None,
            'applicant_name': 'Test Testington',
            'date_accessed': '',
            'application_id': '4c004204-84e1-4f47-b118-c91fbb47a0bf'
        }]

        formatted_search_list = SearchService._format_search_results(mock_search_list)

        self.assertEqual(formatted_search_list, expected_formatted_search_list)
