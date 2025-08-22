from django import forms
from .models import AuditeeResponse
from .models import AuditFinding ,Audit , OrganizationalUnit
from django.contrib.auth.models import User, Group

class AuditeeResponseForm(forms.ModelForm):
    class Meta:
        model = AuditeeResponse
        fields = ['comment', 'evidence_file']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }



class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['title', 'unit', 'end_date']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'})
        }
