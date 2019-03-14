from django import forms
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField

from memoir.models import Memo, Attachment

class MemoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MemoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Memo
        fields = ('to', 'recipients', 'subject', 'mem_priority', 'mem_type', 'commenting_required', 'message', )

    to = AutoCompleteSelectField('user', required=False, help_text=None)
    recipients = AutoCompleteSelectMultipleField('user', required=False, help_text=None)

class UploadFileForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(UploadFileForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control'
			
	class Meta:
		model = Attachment
		fields = ('file_name', 'file',)
        
class MemoReasignForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MemoReasignForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs['readonly'] = True
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Memo
        fields = ('to', 'recipients', 'subject', )

    to = AutoCompleteSelectField('user', required=False, help_text=None)
    recipients = AutoCompleteSelectMultipleField('user', required=False, help_text=None)