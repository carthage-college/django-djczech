# -*- coding: utf-8 -*-

from django import forms

from djtools.fields.validators import MimetypeValidator

class ChequeDataForm(forms.Form):

    import_date = forms.DateField()
    bank_data = forms.FileField(
        max_length = "768",
        validators=[MimetypeValidator('text/plain')],
        help_text = '<p>File format: .csv file</p>'
    )

    class Meta:
        pass
