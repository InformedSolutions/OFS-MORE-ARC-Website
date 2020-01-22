import logging

import requests

from django.conf import settings
from requests import RequestException
from django.utils.http import urlencode

logger = logging.getLogger(__name__)


def get_individual_search_results(query_params):
    """
    Integration method for getting list of individuals which match search criteria
    :param query_params: dictionary of search criteria
    :return IndividualSearchResponse object containing results of the search
    """
    logger.debug(f"Getting individuals from integration-adapter")

    successful = False
    found = False
    individuals = None

    request_url = f"{settings.INTEGRATION_ADAPTER_URL}/api/v1/individuals-search/?{urlencode(query_params)}"

    try:
        api_response = requests.get(request_url, verify=False)

        if api_response.status_code:
            successful = True

            if api_response.status_code == 200:
                logger.debug(f"Received individual search results from adapter")
                deserialized_response = api_response.json()
                individuals = deserialized_response['Individual']
                found = True
        else:
            logger.debug(f"Problem with received results from adapter")
    except (AttributeError, RequestException):
        logger.debug("Problem with connection with integration adapter")

    return IndividualSearchResponse(successful, found, individuals)


class IndividualSearchResponse:
    """
    Response class for getting individuals
    if the response is successful and individuals are found it will contain a list of individuals
    matching the search criteria
    """
    def __init__(self, successful=None, found=None, individuals=None):
        self.individuals = individuals
        self.successful = successful
        self.found = found
