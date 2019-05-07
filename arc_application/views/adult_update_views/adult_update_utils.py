from arc_application.services.db_gateways import HMGatewayActions

from .adult_update_summary import load_json


def get_adult_update_summary_variables(adult_id):
    """
    Method to format the output from load_json, whose output is an ordered list of tables for adults' updates tables.
    This method essentially splits out these tables per adult so that only a single adult's information is returned.
    """
    dpa_auth_id = HMGatewayActions().read('adult', params={'adult_id': adult_id}).record['token_id']
    application_reference = HMGatewayActions().read('dpa-auth', params={'token_id': dpa_auth_id}).record['URN']

    adult_tables = load_json(adult_id)

    variables = {
        'application_reference': application_reference,
        'json': adult_tables
    }

    if len(adult_tables) == 0:
        raise ValueError("Adult with adult_id: %s not found in summary data." % adult_id)
    else:
        return variables
