#!/bin/bash
#
# Given a file containing one URS per line, this script will download the svg file
# from Embassy 3 and then upload it to Embassy 4.
#
# Usage:   ./copy_missing_svg_files.sh [file] [env]
# Example: ./copy_missing_svg_files.sh file.txt prod

# set the file based on the first argument and the environment based on the second argument
file_list=$1
env=$2

# bucket for both Embassy 3 and 4
bucket_name=""

# parameters for Embassy 3
embassy3_secret=""
embassy3_s3_key=""

# parameters for Embassy 4
embassy4_secret=""
embassy4_s3_key=""

function s3DownloadAndUpload
{
  # set the file based on the first argument and the object (environment) based on the second argument
  file=$1
  env=$2

  #############################
  # steps to download the file
  #############################

  # set the name of the file to be copied and the S3 path
  extension=".svg.gz"
  urs="${file}${extension}"
  path=$env/${urs:0:3}/${urs:3:2}/${urs:5:2}/${urs:7:2}/${urs:9:2}

  # get the current date to calculate the signature
  embassy3_date=`date +'%a, %d %b %Y %H:%M:%S %z'`

  # calculate the signature to be sent as a header
  content_type="application/octet-stream"
  embassy3_string_to_sign="GET\n\n${content_type}\n${embassy3_date}\n/${bucket_name}/${path}/${urs}"
  embassy3_signature=$(echo -en "${embassy3_string_to_sign}" | openssl sha1 -hmac "${embassy3_secret}" -binary | base64)

  # download the file
  curl -H "Host: s3.embassy.ebi.ac.uk/${bucket_name}" \
       -H "Date: ${embassy3_date}" \
       -H "Content-Type: ${content_type}" \
       -H "Authorization: AWS ${embassy3_s3_key}:${embassy3_signature}" \
       "https://s3.embassy.ebi.ac.uk/${bucket_name}/${path}/${urs}" -o "embassy-3/${urs}"

  ###########################
  # steps to upload the file
  ###########################

  # get the current date to calculate the signature and also to pass to S3
  embassy4_date=`date -R -u`

  # calculate the signature to be sent as a header
  embassy4_string_to_sign="PUT\n\n${content_type}\n${embassy4_date}\n/${bucket_name}/${path}/${urs}"
  embassy4_signature=$(echo -en "${embassy4_string_to_sign}" | openssl sha1 -hmac "${embassy4_secret}" -binary | base64)

  if test -f "embassy-3/${urs}"; then
    # upload file
    curl -X PUT -T "embassy-3/${urs}" \
         -H "Host: uk1s3.embassy.ebi.ac.uk/${bucket_name}" \
         -H "Date: ${embassy4_date}" \
         -H "Content-Type: ${content_type}" \
         -H "Authorization: AWS ${embassy4_s3_key}:${embassy4_signature}" \
         "https://uk1s3.embassy.ebi.ac.uk/${bucket_name}/${path}/${urs}"
    # add to the list of copied files
    echo "${urs}" >> copied/copied_${file_list}
  else
    # file not found
    echo "${file}" >> file_not_copied.txt
  fi
}

# loop through the file
while IFS="" read -r p || [ -n "$p" ]
do
  s3DownloadAndUpload "$p" "$env"
done < "$file_list"
