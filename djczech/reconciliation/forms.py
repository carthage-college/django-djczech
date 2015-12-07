# -*- coding: utf-8 -*-

from django import forms

class ChequeDataForm(forms.Form):

    import_date = forms.DateField()
    bank_data = forms.FileField(
        max_length = "768",
        help_text = '''
            <p>Please upload a TSV (Tab Separated file) where the
            field values are separated by tabs.</p>
        '''
    )

    class Meta:
        pass
