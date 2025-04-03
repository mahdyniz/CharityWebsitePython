from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount', 'donor_name', 'donor_email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        } 