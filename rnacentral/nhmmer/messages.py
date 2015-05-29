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

"""
API messages and status codes.
"""

from settings import MIN_LENGTH, MAX_LENGTH


messages = {

    # submit endpoint
    'submit': {
        400: {
            'too_short': {
                'message': 'Sequence cannot be shorter than %i nucleotides' % MIN_LENGTH,
            },
            'too_long': {
                'message': 'Sequence cannot be longer than %i nucleotides' % MAX_LENGTH,
            },
            'no_sequence': {
                'message': 'Sequence cannot be empty',
            },
        },
        500: {
            'message': 'Unknown error',
        },
    },

    # get status endpoint
    'status': {
        400: {
            'message': 'Job id not specified',
        },
        404: {
            'message': 'Job not found',
        },
        500: {
            'message': 'Unknown error',
        },
    },

    # cancel job endpoint
    'cancel': {
        200: {
            'message': 'Job cancelled',
        },
        400: {
            'message': 'Job id not specified',
        },
        404: {
            'message': 'Job not found',
        },
        500: {
            'message': 'Unknown error',
        },
    },
}
