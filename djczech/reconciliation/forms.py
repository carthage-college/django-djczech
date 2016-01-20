# -*- coding: utf-8 -*-

from django import forms

#from djtools.fields.validators import MimetypeValidator

#validators=[MimetypeValidator('text/csv')],

class ChequeDataForm(forms.Form):

    import_date = forms.DateField()
    bank_data = forms.FileField(
        max_length = "768",
        help_text = '<p>File format: .csv file</p>'
    )

    class Meta:
        pass
