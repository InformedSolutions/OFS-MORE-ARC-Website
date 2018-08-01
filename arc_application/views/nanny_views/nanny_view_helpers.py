def parse_date_of_birth(dob_str):
    '''
    Converts dob_str to it's corresponding parts.
    :param dob_str: The date of birth in assumed format YYYY-MM-DD
    :return: A dictionary containing strings birth_year, birth_month and birth_day.
    '''

    if len(dob_str) == 10:
        birth_year = dob_str[:4]
        birth_month = dob_str[5:-3]
        birth_day = dob_str[-2:]

        dob_dict = {
            'birth_year': birth_year,
            'birth_month': birth_month,
            'birth_day': birth_day
        }

        return dob_dict

    else:
        raise ValueError("{0} is not a valid dob_str, the length should be 10 but it is {1}".format(dob_str, len(dob_str)))
