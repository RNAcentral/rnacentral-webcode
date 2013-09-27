from django import forms
from rnacentral import local_settings

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)

    def send_email(self):
	    subject = '[RNAcentral Contact Us] ' + self.cleaned_data['subject']
	    message = self.cleaned_data['message']
	    sender = self.cleaned_data['sender']
	    recipients = [ local_settings.EMAIL_RNACENTRAL_HELPDESK ]
	    if self.cleaned_data['cc_myself']:
	        recipients.append(sender)
	    from django.core.mail import send_mail
	    send_mail(subject, message, sender, recipients)
