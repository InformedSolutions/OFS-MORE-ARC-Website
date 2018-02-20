"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --

@author: Informed Solutions
"""

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserModel
from govuk_forms.forms import GOVUKForm

from .models import ArcReview
from .views import has_group, authenticate, capfirst


class CheckBox(GOVUKForm):
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    information_correct_declare = forms.BooleanField(label='This information is correct')

class CommentsForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    comments = forms.CharField(label='Comments', required=False, widget=forms.TextInput(attrs={'size': 80}))

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: email form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(CommentsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if ArcReview.objects.filter(application_id=self.application_id_local).count() > 0:
            rev = ArcReview.objects.get(application_id=self.application_id_local)
            self.fields['comments'].initial = rev.comments

    def clean_comments(self):
        comments = self.cleaned_data['comments']
        # RegEx for valid e-mail addresses

        return comments

