"""
Link dict to associate tables with their corresponding view for change link reversal
"""
link_dict = {
    'Your sign in details': 'contact_summary',
    'Type of childcare': 'type_of_childcare_age_groups',
    'Your name and date of birth': 'personal_details_summary',
    'Individual lookup': 'personal_details_summary',
    'Previous names': 'personal_details_summary',
    'Your home and childcare address': 'personal_details_summary',
    'Previous addresses': 'personal_details_summary',
    'Your children': 'personal_details_summary',
    'First aid training': 'first_aid_training_summary',
    'Childcare training': 'childcare_training_check_summary',
    'Health declaration booklet': 'health_check_answers',
    'Criminal record checks': 'dbs_check_summary',
    'Adults in the home where childcare takes place': 'other_people_summary',
    'Children in the home where childcare takes place': 'other_people_summary',
    'First reference': 'references_summary',
    'Second reference': 'references_summary'
}