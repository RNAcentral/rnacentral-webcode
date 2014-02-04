"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
        recipients = [local_settings.EMAIL_RNACENTRAL_HELPDESK]
        if self.cleaned_data['cc_myself']:
            recipients.append(sender)
        from django.core.mail import send_mail
        send_mail(subject, message, sender, recipients)
