import datetime

from django import forms

from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from catalog.models import BookInstance


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text='Enter a date between now and 4 weeks (default 3).')

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data

class UpdateBookInstanceModelForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ['book', 'language', 'imprint', 'status', 'borrower', 'due_back']
        labels = {'due_back': 'Renewal date'}

    def clean_due_back(self):
        data = self.cleaned_data['due_back']
        if data is not None:
            if data < datetime.date.today():
                raise ValidationError(_('Invalid date - Renewal date in past'))

            if data > datetime.date.today() + datetime.timedelta(weeks=4):
                raise ValidationError(_('Invalid date - Renewal date more than 4 weeks ahead'))
        return data
