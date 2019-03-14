from django import forms
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField

from .models import Notice, Listing
from profiles.models import City, Department, Office

class NoticeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NoticeForm, self).__init__(*args, **kwargs)
        self.fields['office'].queryset = Office.objects.none()
        self.fields['department'].queryset = Department.objects.none()
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['office'].queryset = Office.objects.filter(city_id=city_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['office'].queryset = self.instance.city.office_set.order_by('name')
        
        if 'office' in self.data:
            try:
                office_id = int(self.data.get('office'))
                self.fields['department'].queryset = Department.objects.filter(office_id=office_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['department'].queryset = self.instance.office.department_set.order_by('name')

    class Meta:
        model = Notice
        fields = ('name', 'priority', 'city', 'office', 'department', 'description', 'expiry')
        widgets = {
            'expiry': forms.DateInput(attrs={'class':'datepicker','type': 'date'}),
        }


class NoticeUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NoticeUpdateForm, self).__init__(*args, **kwargs)
        # self.fields['office'].queryset = Office.objects.none()
        # self.fields['department'].queryset = Department.objects.none()
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Notice
        fields = ('name', 'priority', 'city', 'office', 'department', 'description', 'expiry')
        widgets = {
            'expiry': forms.DateInput(attrs={'class':'datepicker','type': 'date'}),
        }


class ListingUpdate(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('name', 'description')

