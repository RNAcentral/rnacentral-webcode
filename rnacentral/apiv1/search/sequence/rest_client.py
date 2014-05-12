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
    A default exception class for sequence search error handling.
    """
    def __init__(self, message='Internal error'):
        self.message = message


class ResultsUnavailableError(Exception):
    """
    An exception raised when search results are not available or have expired.
    """
    def __init__(self):
        self.message = ('Results not available or expired. '
                        'Please repeat the search')


class InvalidSequenceError(Exception):
    """
    An exception raised when the sequence is not valid.
    """
    def __init__(self):
        self.message = 'Invalid sequence'


class StatusNotFoundError(Exception):
    """
    An exception raised when the status is not found when session have expired.
    """
    def __init__(self):
        self.message = 'Query status not found'


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
        base_url = 'http://www.ebi.ac.uk/ena/search'
        # ENA Non-coding sequence collection name, url encoded
        collection = '/All Sequences/All EMBL-Bank/Non-coding'.\
                     replace('/', '%2F').replace(' ', '%20')
        # ENA results columns in tab-delimited format
        self.field_names = ['accession', 'e_value', 'identity', 'target_length',
                            'query_range', 'target_range','alignment_length',
                            'target_length','identities', 'gaps',
                            'formatted_alignment']
        # ENA REST API endpoints
        self.endpoints = {
            'search':  base_url + '/executeSearch?Sequence={sequence}&'
                                  'type=sensitive&'
                                  'collection=' + collection,
            'status':  base_url + '/searchStatus?job_id={job_id}&display=json',
            'results': base_url + '/searchResults?job_id={job_id}&'
                                  'length={length}&offset={offset}&'
                                  'display=json&'
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

    def __raise_error(self, message='', exception_class=SequenceSearchError):
        """
        Internal method for error reporting.
        Raise an error after logging the message.
        """
        if message:
            self.logger.error(message)
            raise exception_class(message)
        else:
            raise exception_class()

    def submit_query(self, sequence):
        """
        Submit a sequence to ENA and return job id and cookies.
        job_id and jsession_id are both required for identifying the query.

        Exception types:
            InvalidSequenceError - for invalid sequences
            SequenceSearchError  - all other errors.
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
                self.__raise_error(message=message)

        def validate_response(response):
            """
            Make sure that this is not an error response.
            """
            if response.status_code != 200 or 'Tomcat' in response.text:
                message = 'Got error instead of status url: {error}'.\
                          format(error=response.text)
                self.__raise_error(message=message)

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
                self.__raise_error(message=message)

        def get_jsession_id(cookies):
            """
            Get session id from the cookies dictionary
            returned by the ENA server.
            """
            if self.JSESSIONID in cookies:
                return cookies[self.JSESSIONID]
            else:
                message = 'Session id not found'
                self.__raise_error(message=message)

        sequence = format_sequence(sequence)
        if is_valid_sequence(sequence):
            response = send_request(sequence)
            validate_response(response)
            job_id = get_job_id(response.text)
            jsession_id = get_jsession_id(response.cookies)
        else:
            self.__raise_error(exception_class=InvalidSequenceError)
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

        Exception types:
            SequenceSearchError - if there is a persisting connection problem.
            StatusNotFoundError - if query status was not found on the server.
        """
        def get_status_response():
            """
            Retrieve status string from ENA, retry several times if there are
            connection problems.
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
                        'on attempt {attempt} with error: {error}'.format(
                        attempt=attempt, error=e.message))
                    time.sleep(DELAY_BEFORE_RETRY)
                    attempt += 1
            if attempt > RETRY_ATTEMPTS:
                message = 'Getting status failed after {attempt} attempts'.\
                          format(attempt=attempt)
                self.__raise_error(message=message) # SequenceSearchError
            else:
                return response

        def validate_response(response):
            """
            Make sure that this is not an error response.
            """
            if response.status_code == 404 or 'not found in session' in response.text:
                self.__raise_error(exception_class=StatusNotFoundError)

        response = get_status_response()
        validate_response(response)
        count = response.json()['alignment_count']
        if response.json()['status'] == 'COMPLETE':
            status = 'Done'
        else:
            status = 'In progress'
        return (status, count)

    # TODO fix length default which fails tests for results with < 10 hits
    def get_results(self, job_id, jsession_id, length=10, offset=1):
        """
        Retrieve job results in json format.

        Exception types:
            ResultsUnavailableError - when results are not available
            SequenceSearchError     - all other erros
        """
        try:
            url = self.endpoints['results'].format(job_id=job_id,
                                                   offset=offset,
                                                   length=length)
            r = requests.get(url, cookies={self.JSESSIONID: jsession_id})
        except RequestException, exc:
            message = 'Results could not be retrieved: ' + exc.message
            self.__raise_error(message=message)
        else:
            if r.status_code == 500:
                raise ResultsUnavailableError()
        return r.json()

    def search(self, sequence=''):
        """
        Perform sequence search synchronously.
        """
        results = status = None
        (job_id, jsession_id) = self.submit_query(sequence)
        while status != 'Done':
            time.sleep(self.refresh_rate)
            (status, count) = self.get_status(job_id, jsession_id)
        results = self.get_results(job_id, jsession_id)
        print 'Found {0} results'.format(len(results))
        if results:
            print 'First result:'
            print results[0]
        return results
