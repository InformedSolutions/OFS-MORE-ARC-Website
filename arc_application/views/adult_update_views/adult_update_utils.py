from .adult_update_summary import load_json


def get_adult_update_summary_variables(application_id, adult_id):
    """
    Method to format the output from load_json, whose output is an ordered list of tables for adults' updates tables.
    This method essentially splits out these tables per adult so that only a single adult's information is returned.
    """
    all_adult_tables = load_json(application_id)

    single_adult_tables = [table for table in all_adult_tables if table[0]['id'] == adult_id]

    if len(single_adult_tables) == 0:
        raise ValueError("Adult with adult_id: %s not found in summary data for application_id: %s" % (adult_id, application_id))
    else:
        return single_adult_tables
