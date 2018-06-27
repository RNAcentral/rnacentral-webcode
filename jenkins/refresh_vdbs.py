from __future__ import print_function

import argparse
import paramiko
import re


"""
This script creates a latest snapshot of PRO database and refreshes
fb1 and pg databases from it.

I'm not using fabric for this cause there's a crazy bug in it - passing the
password to fabfile on remote machine from command line doesn't work and fabric
attempts to prompt for password, even if password is given: 
https://github.com/fabric/fabric/issues/1513. Anyways, fabric's API is poorly 
designed, so let's give a go to raw python.

Examples:

python refresh_vdbs.py --password mysecretpassword
python refresh_vdbs.py --keyfile /path/to/private/ssh/key
"""


def connect(host, user, password=None, keyfile=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password is not None:
        client.connect(hostname=host, username=user, password=password, port=22)
    elif keyfile is not None:
        pkey = paramiko.RSAKey.from_private_key_file(keyfile)
        client.connect(hostname=host, username=user, pkey=pkey, port=22)
    return client


if __name__ == "__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Refresh remote databases')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--password', type=str, help='password for logging-in, if ssh private key is not used for logging in')
    group.add_argument('--keyfile', type=str, help='keyfile path for passwordless login')
    args = parser.parse_args()

    password = open(args.password).read().strip()
    print("password = %s" % password)
    client = connect(host='pg-001.ebi.ac.uk', user='burkov', password=password)

    # find the latest snapshot on PG
    stdin, stdout, stderr = client.exec_command('sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_list_snapshots.sh -d pgsql-dlvmpub1-010.ebi.ac.uk | tail -1')
    snapshot = stdout.read()
    # if stdout and stderr were passed together, we would've had to filter them as bash curses about absence of /home
    # snapshot = re.search("\d\d\d\d\-\d\d\-\d\d\s\d\d\:\d\d$", output).group(0)  # e.g. 2018-06-26 11:16
    print(snapshot + stderr.read())

    # refresh PG from the latest snapshot
    stdin, stdout, stderr = client.exec_command("sudo -u dxrnacen /nfs/dbtools/delphix/postgres/ebi_refresh_vdb.sh -d pgsql-dlvmpub1-010.ebi.ac.uk -S '%s'" % snapshot)
    print(stdout.read() + stderr.read())

    client.close()
