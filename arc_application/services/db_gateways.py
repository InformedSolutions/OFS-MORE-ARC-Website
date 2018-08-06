import os
import json

import requests


class DBGatewayActions:
    """
    Base class for handling all requests to Database gateway services at specified target_url_prefix.
    """
    target_url_prefix = None

    def list(self, endpoint, params):
        query_params = ''.join(['&' + key + '=' + value for key, value in params.items()])

        response = requests.get(self.target_url_prefix + endpoint + '/?' + query_params)

        if response.status_code == 200:
            response.record = json.loads(response.text)

        return response

    def read(self, endpoint, params):
        if endpoint == 'childcare-address':
            response = requests.get(self.target_url_prefix + endpoint + '/' + params['childcare_address_id'] + '/', data=params)
        else:
            response = requests.get(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params)

        if response.status_code == 200:
            response.record = json.loads(response.text)

        return response

    def create(self, endpoint, params):
        response = requests.post(self.target_url_prefix + endpoint + '/', data=params)

        if response.status_code == 201:
            response.record = json.loads(response.text)

        return response

    def patch(self, endpoint, params):
        response = requests.patch(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params)

        if response.status_code == 200:
            response.record = json.loads(response.text)

        return response

    def put(self, endpoint, params):
        if endpoint == 'childcare-address':
            response = requests.put(self.target_url_prefix + endpoint + '/' + params['childcare_address_id'] + '/', data=params)
        else:
            response = requests.put(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params)

        if response.status_code == 200:
            response.record = json.loads(response.text)

        return response

    def delete(self, endpoint, params):
        return requests.delete(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params)


class IdentityGatewayActions(DBGatewayActions):
    """
    Class for handling all requests to the Identity Gateway service.
    """
    target_url_prefix = os.environ.get('APP_IDENTITY_URL') + 'api/v1/'


class NannyGatewayActions(DBGatewayActions):
    """
    Class for handling all requests to the Nanny Gateway service.
    """
    target_url_prefix = os.environ.get('APP_NANNY_GATEWAY_URL') + '/api/v1/'
