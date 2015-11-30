# -*- coding: utf-8 -*-

from django import forms

class ChequeDataForm(forms.Form):

    import_date = forms.DateField()
    bank_data = forms.FileField(
        max_length = "768",
        help_text = '''
            <p>Please upload a CSV file with values separated
            by tabs or pipes "|".</p>
        '''
    )

    class Meta:
        pass
