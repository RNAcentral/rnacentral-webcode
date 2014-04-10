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

import logging
import re
import requests
from requests.exceptions import RequestException
import time


class SequenceSearchError(Exception):
    """
    An exception class for sequence search error handling.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ENASequenceSearchClient(object):
    """
    A class for interacting with the ENA REST Sequence Search API.

    This class will throw SequenceSearchError exceptions with error messages,
    which should be properly handled by the calling code.
    """

    def __init__(self):
        """
        Configurable parameters.
        """
        # ENA REST API base url (NB! no trailing slash)
        base_url = 'http://jweb-1a:21160/ena/search'
        # ENA Non-coding sequence collection name, url encoded
        collection = '/All Sequences/All EMBL-Bank/Non-coding'.\
                     replace('/', '%2F')
        # ENA results columns in tab-delimited format
        self.field_names = ['accession', 'e_value', 'identity'] #, 'formatted_alignment']
        # ENA REST API endpoints
        self.endpoints = {
            'search':  base_url + '/executeSearch?Sequence={sequence}&'
                                  'collection=' + collection,
            'status':  base_url + '/searchStatus?job_id={job_id}',
            'results': base_url + '/searchResults?job_id={job_id}&'
                                  'fields=' + ','.join(self.field_names),
        }
        # ENA minimum word size that can be searched
        self.min_length = 12
        # set to infinity for now. TODO: put the real cutoff
        self.max_length = float("inf")
        # ENA-generated session id cookie
        self.JSESSIONID = 'JSESSIONID'
        # refresh interval for retrieving results
        self.refresh_rate = 2
        # get logger instance
        self.logger = logging.getLogger(__name__)

    def __raise_error(self, message):
        """
        Internal method for error reporting.
        Raise the error after logging the message.
        """
        self.logger.error(message)
        raise SequenceSearchError(message)

    def submit_query(self, sequence):
        """
        Submit a sequence to ENA and return job id and cookies.
        job_id and jsession_id are both required for identifying the query.
        Throws SequenceSearchError.
        """
        job_id = jsession_id = None

        def format_sequence(sequence):
            """
            Prepare the query sequence for submission.
            """
            return sequence.upper().replace('U', 'T').replace(' ', '')

        def is_valid_sequence(sequence):
            """
            Validate sequence before submission.
            """
            seq_len = len(sequence)
            if seq_len >= self.min_length and seq_len < self.max_length:
                return True
            else:
                return False

        def send_request(sequence):
            """
            Submit the sequence to ENA, return the response object
            with a status url and session cookies.
            """
            try:
                return requests.get(self.endpoints['search'].\
                                    format(sequence=sequence))
            except RequestException, exc:
                message = 'Query could not be submitted: {error}'.\
                          format(error=exc.message)
                self.__raise_error(message)

        def validate_response(text):
            """
            Make sure that this is not a Tomcat error message.
            """
            if 'Tomcat' in text:
                message = 'Tomcat error instead of status url: {error}'.\
                          format(error=text)
                self.__raise_error(message)

        def get_job_id(status_url):
            """
            Capture job_id from the returned status url using regex.
            """
            match = re.search(r'job_id=([0-9A-z\-]+)', status_url)
            if match:
                job_id = match.group(1)
                return job_id
            else:
                message = 'Job id not found in url {status_url}'.\
                          format(status_url=status_url)
                self.__raise_error(message)

        def get_jsession_id(cookies):
            """
            Get session id from the cookies dictionary
            returned by the ENA server.
            """
            if self.JSESSIONID in cookies:
                return cookies[self.JSESSIONID]
            else:
                message = 'Session id not found'
                self.__raise_error(message)

        sequence = format_sequence(sequence)
        if is_valid_sequence(sequence):
            response = send_request(sequence)
            validate_response(response.text)
            job_id = get_job_id(response.text)
            jsession_id = get_jsession_id(response.cookies)
            print job_id
            print jsession_id
        else:
            self.__raise_error('Invalid sequence')
        return (job_id, jsession_id)

    def get_status(self, job_id, jsession_id):
        """
        Get job status.
        Example status strings:
            SEARCHING   Searching against 10,254,071 target sequences (5,356,715,565 base pairs)    108 108 0  # pylint: disable=line-too-long
            COMPLETE    Searching against 10,258,876 target sequences (5,358,703,279 base pairs)    108 108 35 # pylint: disable=line-too-long
        Return values:
            "Done" if results are available
            "In progress"  if results are not yet available
        Throws SequenceSearchError.
        """
        def get_status_string():
            """
            Retrieve status string from ENA, retry several times on error.
            """
            RETRY_ATTEMPTS = 3
            DELAY_BEFORE_RETRY = 0.5
            attempt = 1
            while attempt <= RETRY_ATTEMPTS:
                try:
                    response = requests.get(self.endpoints['status'].format(job_id=job_id),
                                            cookies={self.JSESSIONID: jsession_id})
                    break
                except RequestException, exc:
                    self.logger.warning('Getting query status failed '
                        'on attempt {attempt} with error: {error}'.\
                        format(attempt=attempt, error=e.message))
                    time.sleep(DELAY_BEFORE_RETRY)
                    attempt += 1
            if attempt > RETRY_ATTEMPTS:
                message = 'Getting status failed after {attempt} attempts'.\
                          format(attempt=attempt)
                self.__raise_error(message)
            else:
                return response.text

        def validate_response(status_string):
            """
            Check the status string to make sure
            that this is not a Tomcat error message.
            """
            if 'not found in session' in status_string:
                message = 'Job could not be found'
                self.__raise_error(message)

        status_string = get_status_string()
        validate_response(status_string)
        # TODO parse status_string to get the total number of results
        if 'COMPLETE' in status_string:
            return 'Done'
        else:
            return 'In progress'

    def get_results(self, job_id, jsession_id):
        """
        Retrieve job results in tab delimited format.
        """
        results = ''
        try:
            r = requests.get(self.endpoints['results'].format(job_id=job_id),
                             cookies={self.JSESSIONID: jsession_id})
        except RequestException, exc:
            print 'Results could not be retrieved: ' + exc.message
        else:
            print r.text
            results = r.text
        return results

    def format_results(self, results):
        """
        Convert results to json.
        """
        data = []
        for line in results.split('\n'):
            if line == '':
                continue
            fields = line.split('\t')
            entry = {}
            for i, field in enumerate(fields):
                entry[self.field_names[i]] = field
            data.append(entry)
        return data

    def search(self, sequence=''):
        """
        Perform sequence search synchronously.
        """
        results = status = None
        (job_id, jsession_id) = self.submit_query(sequence)
        while status != 'Done':
            time.sleep(self.refresh_rate)
            status = self.get_status(job_id, jsession_id)
        tsv_results = self.get_results(job_id, jsession_id)
        json_results = self.format_results(tsv_results)
        results = json_results
        for entry in json_results:
            print entry
        return results
