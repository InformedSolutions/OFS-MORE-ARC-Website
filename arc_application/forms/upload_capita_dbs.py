
from django.forms import FileField
from govuk_forms.forms import GOVUKForm


class UploadCapitaDBSForm(GOVUKForm):
    capita_list_file = FileField(required=True,
                                 error_messages={
                                     'required': 'No file chosen'
                                 })
