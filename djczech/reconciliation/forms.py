# -*- coding: utf-8 -*-

from django import forms

class ChequeDataForm(forms.Form):

    bank_data = forms.FileField(
        max_length="768"
    )

    class Meta:
        pass
