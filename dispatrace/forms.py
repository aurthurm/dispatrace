from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout

from dispatrace.validators import DispatracePasswordValidator

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,                                         
        help_text='Required'
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,                                         
        help_text='Required'
    )
    email = forms.EmailField(
        max_length=254, 
        help_text='Required. Provide a valid email'
    )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].validators.append(DispatracePasswordValidator)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
