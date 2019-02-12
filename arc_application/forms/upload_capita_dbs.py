from django.forms import FileField, ValidationError
from govuk_forms.forms import GOVUKForm


class UploadCapitaDBSForm(GOVUKForm):
    error_summary_title = 'There was a problem'

    valid_extensions = (
        '.xlxs',
        '.csv'
    )

    capita_list_file = FileField(allow_empty_file=True, required=False, label='Upload a file')

    def clean_capita_list_file(self):
        capita_list_file = self.data['capita_list_file']

        if capita_list_file is None:
            raise ValidationError('No file chosen')

        if not any([capita_list_file.lower().endswith(ext) for ext in self.valid_extensions]):
            raise ValidationError('The file must be .csv or .xlxs')

        return capita_list_file
