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

##############################################################################
# RNAcentral FTP export using the EBI LSF cluster.
#
# Requires UCSC tools (bedToBigBed and fetchChromSizes)
#
# Usage:
# . ftp_export_parallel.sh /path/to/destination/directory /path/to/ucsc/tools
##############################################################################

destination=$1 # first command line argument
ucsc_tools=$2 # second command line argument

# make a directory for LSF log files if it does not exist
mkdir -p logs

# create the output directory if it does not exist
mkdir -p $destination

# xrefs
bsub -o logs/xrefs_lsfreport.txt -e logs/xrefs_output.txt python manage.py ftp_export -f xrefs -d $destination

# fasta
bsub -o logs/fasta_lsfreport.txt -e logs/fasta_output.txt python manage.py ftp_export -f fasta -d $destination

# md5
bsub -o logs/md5_lsfreport.txt -e logs/md5_output.txt python manage.py ftp_export -f md5 -d $destination
