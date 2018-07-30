import os
import json

import requests


class DBGatewayActions:
    target_url_prefix = None

    def list(self, endpoint, params):
        response = requests.get(self.target_url_prefix + endpoint + '/', data=params)

        if response.status_code == 200:
            response.record = json.loads(requests.get(self.target_url_prefix + endpoint + '/', data=params).text)

        return response

    def read(self, endpoint, params):
        return json.loads(requests.get(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params).text)

    def create(self, endpoint, params):
        response = requests.post(self.target_url_prefix + endpoint + '/', data=params)

        if response.status_code == 201:
            response.record = json.loads(requests.get(self.target_url_prefix + endpoint + '/', data=params).text)

        return response

    def patch(self, endpoint, params):
        response = requests.patch(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params)

        if response.status_code == 200:
            response.record = json.loads(requests.get(self.target_url_prefix + endpoint + '/', data=params).text)

        return response

    def put(self, endpoint, params):
        response = requests.put(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params)

        if response.status_code == 200:
            response.record = json.loads(requests.get(self.target_url_prefix + endpoint + '/', data=params).text)

        return response

    def delete(self, endpoint, params):
        return requests.delete(self.target_url_prefix + endpoint + '/' + params['application_id'] + '/', data=params)


class IdentityGatewayActions(DBGatewayActions):
    target_url_prefix = os.environ.get('APP_IDENTITY_URL') + 'api/v1/'


class NannyGatewayActions:
    target_url_prefix = os.environ.get('APP_NANNY_GATEWAY_URL') + '/api/v1/'
