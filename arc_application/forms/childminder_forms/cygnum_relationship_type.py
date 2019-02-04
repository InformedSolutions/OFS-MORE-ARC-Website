from django import forms

from govuk_forms.forms import GOVUKForm


class CygnumRelationshipType(GOVUKForm):
    """
    GOV.UK form for ARC user to select the relationship type for a household member.
    """
    auto_replace_widgets = True

    relationship_choices = (
        (None, ''),
        ('Acting manager', 'Acting manager'),
        ('Boyfriend', 'Boyfriend'),
        ('Brother', 'Brother'),
        ('Brother in law', 'Brother in law'),
        ('Chairperson', 'Chairperson'),
        ('Childminding Assistant', 'Childminding Assistant'),
        ('CIO Member', 'CIO Member'),
        ('Co-Childminder', 'Co-Childminder'),
        ('Committee Member', 'Committee Member'),
        ('Co-Ordinator', 'Co-Ordinator'),
        ('Cousin', 'Cousin'),
        ('Daughter', 'Daughter'),
        ('Deputy Manager', 'Deputy Manager'),
        ('Director', 'Director'),
        ('Father', 'Father'),
        ('Father in Law', 'Father in Law'),
        ('Fiancé', 'Fiancé'),
        ('Foster Child', 'Foster Child'),
        ('Friend', 'Friend'),
        ('Governor', 'Governor'),
        ('Granddaughter', 'Granddaughter'),
        ('Grandson', 'Grandson'),
        ('Head Teacher', 'Head Teacher'),
        ('Home Childcarer', 'Home Childcarer'),
        ('Husband', 'Husband'),
        ('Job Share', 'Job Share'),
        ('Joint Manager', 'Joint Manager'),
        ('Lodger', 'Lodger'),
        ('Manager', 'Manager'),
        ('Managing Director', 'Managing Director'),
        ('Mother', 'Mother'),
        ('Mother in Law', 'Mother in Law'),
        ('Named Contact', 'Named Contact'),
        ('Nephew', 'Nephew'),
        ('Niece', 'Niece'),
        ('Owner', 'Owner'),
        ('Partner', 'Partner'),
        ('Person in Charge', 'Person in Charge'),
        ('Secretary', 'Secretary'),
        ('Sister', 'Sister'),
        ('Son', 'Son'),
        ('Son in Law', 'Son in Law'),
        ('Step-Daughter', 'Step-Daughter'),
        ('Step-Son', 'Step-Son'),
        ('Supervisor', 'Supervisor'),
        ('Tenant', 'Tenant'),
        ('Treasurer', 'Treasurer'),
        ('Trustee', 'Trustee'),
        ('Vice Chair', 'Vice Chair'),
        ('Wife', 'Wife'),
    )

    relationship_type = forms.ChoiceField(
        label='Select relationship type',
        error_messages={
            'required': 'You must select a relationship type for this person'
        },
        choices=relationship_choices,
    )

    # checkboxes = [(relationship_type, 'relationship_type'),]

    # for box in checkboxes:
    #     box[0].widget.attrs.update({'data_target': box[1],
    #                                 'aria-controls': box[1],
    #                                 'aria-expanded': 'false'}, )

    # def __init__(self, *args, **kwargs):
        # self.table_keys = kwargs.pop('table_keys')
        # super(CygnumRelationshipType, self).__init__(*args, **kwargs)
        # populate_initial_values(self)
