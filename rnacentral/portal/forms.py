"""
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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
import smtplib
from rnacentral.settings import ADMINS


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=200)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)
    phone = forms.CharField(required=False) # honeypot anti-spam hidden field

    def send_email(self):
        print ADMINS[0][1]
        if self.cleaned_data['phone']:
            # this field would only be filled out by a spam bot
            return False
        subject = '[RNAcentral Contact Us] ' + self.cleaned_data['subject']
        sender = self.cleaned_data['sender']
        recipients = [ADMINS[0][1]]
        if self.cleaned_data['cc_myself']:
            recipients.append(sender)

        message = """From: <{sender}>
To: RNAcentral Help Desk <{helpdesk}>
MIME-Version: 1.0
Content-type: text/html
Subject: {subject}

{message}
""".format(sender=sender, helpdesk=ADMINS[0][1],
           subject=subject, message=self.cleaned_data['message'])

        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, recipients, message)
            return True
        except:
            return False
