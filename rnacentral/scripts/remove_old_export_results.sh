#!/bin/bash

# Copyright [1999-2014] Wellcome Trust Sanger Institute and the EMBL-European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#############################################
# Delete old search export results.
#
# Run by supervisor (see supervisord.conf).
#############################################

if [ -z "$RNACENTRAL_EXPORT_RESULTS_DIR" ]; then
    echo "Need to set RNACENTRAL_EXPORT_RESULTS_DIR"
    exit 1
fi

if [ ! -d "$RNACENTRAL_EXPORT_RESULTS_DIR" ]; then
    echo "RNACENTRAL_EXPORT_RESULTS_DIR does not exist"
    exit 1
fi

cd $RNACENTRAL_EXPORT_RESULTS_DIR

echo 'Starting'

ls

while true
do
    before=`ls | wc -l`
    find . -name \*.gz -type f -mmin +10 -print # -exec rm -rf {} \; # WARNING: be extra careful with this line!
    after=`ls | wc -l`
    count=$((before-after))
    echo $(date -u) "Deleted $count files"
    sleep 60*60 # 60*60 seconds
done
