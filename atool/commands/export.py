'''
Print the information of the current user
'''
from __future__ import unicode_literals, print_function

import json
import logging
import sys
import time

import subprocess as sp
import yaml
import os
import platform
import getpass


log = logging.getLogger('atool.add_role')

DEFAULT_CONTRIB_MODULE_CHANNEL = 'sean'

def run_command(command, fail_message, use_json=True):
    p0 = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    i = 0
    while p0.poll() is None:
        i += 1
        time.sleep(1)
        print('.' * (i % 4), '    ', end='\r')
        sys.stdout.flush()

    output = p0.stdout.read()
    if p0.returncode:
        print('...', 'FAIL')
        print(fail_message, '\n')
        print('    +', output.replace('\n', '\n    + '))
    else:
        print('...', 'OK')
        log.debug(output)

    if use_json:
        return json.loads(output)



def main(args):
    profile_data = run_command(
        ['salt-call', '--local', 'pillar.get', 'profile', '--out=json'],
        'Could not get salt roles'
    )

    profile_data = profile_data['local'].get('data', {})

    profile_roles = run_command(
        ['salt-call', '--local', 'pillar.get', 'roles', '--out=json'],
        'Could not get salt roles'
    )
    profile_roles = profile_roles['local']

    profile = {
       'name': platform.node(),
       'num_nodes': 1,
       'user': getpass.getuser(),
       'head': {'roles': profile_roles},
       'data': profile_data
    }

    print(yaml.safe_dump(profile))
#     name: anaconda_docker_builder
#     provider: aws_east
#     num_nodes: 1
#     node_id: ami-1ccae774 # Amazon Linux AMI 2015.03.0 x86_64 PV EBS
#     node_type: m1.large
#     user: ec2-user
#     conda_channels:
#       - anaconda-cluster-contrib
#       - anaconda-cluster
#       - defaults
#
#     head:
#       roles:
#         - anaconda-builder.docker
#     # compute:
#     #   roles:
#     #     - anaconda-builder
#     #     - docker
#     data:
#       anaconda_builder:
#         token: se-95276e71-5d8f-4465-b8ea-dafc80581bca
#         queue: binstar/public
#         workers: 4



def add_parser(subparsers):
    '''
    '''
    parser = subparsers.add_parser('export',
                                      help='Export A profile',
                                      description=__doc__)

    parser.set_defaults(main=main)

