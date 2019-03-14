from django import forms
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField

from .models import Fuel

class FuelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FuelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Fuel
        fields = (
            'fuel_type', 'priority', 'origin', 'destination', 'date_required', 'amount', 'reason', 'registration', 'assessor', 'approver'
        )
        widgets = {
          'reason': forms.Textarea(attrs={'rows':2, 'cols':15}),
        }

    assessor = AutoCompleteSelectField('users', required=False, help_text=None)
    approver = AutoCompleteSelectField('users', required=False, help_text=None)

class FuelReasignForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FuelReasignForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Fuel
        fields = ('assessor', 'approver', )

    assessor = AutoCompleteSelectField('users', required=False, help_text=None)
    approver = AutoCompleteSelectField('users', required=False, help_text=None)