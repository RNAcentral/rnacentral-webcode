cd ../rnacentral
SNAPSHOT="2018-06-25 10:13"
echo $SNAPSHOT
echo $1
fab pg --password=$1 refresh_pg:snapshot='$SNAPSHOT'