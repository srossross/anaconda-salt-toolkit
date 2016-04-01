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

from atool.salt_utils import enable_salt_state, update_profile_pillar, update_roles_pillar

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


def install_conda_salt_module(rolename, use_local, channel):
    conda_module = 'salt-{}'.format(rolename.split('.')[0])
    conda_command = ['conda', 'install', '--json', conda_module]

    if use_local:
        conda_command.append('--use-local')
    for channel in channel:
        conda_command.extend(['-c', channel])


    print("Installing salt module {} from conda ...".format(conda_module))
    log.debug(' '.join(conda_command))
    run_command(conda_command, 'Conda could not install the role. Conda output::', False)


def get_profile_data(keys):
    profile_data = {}
    for item in keys:
        if '=' not in item:
            log.warn('Invalid profile data from command line: {}'.format(item))
            continue

        key, value = item.split('=', 1)
        value = yaml.safe_load(value)
        profile_data[key] = value

    return profile_data




def main(args):
    print("Adding Role", args.rolename)

    profile_data = get_profile_data(args.keys)
    install_conda_salt_module(args.rolename, args.use_local, args.channel)
    update_profile_pillar(args.rolename, profile_data)
    enable_salt_state(args.rolename)

    update_roles_pillar(args.rolename, profile_data)




def add_parser(subparsers):
    '''
    '''
    parser = subparsers.add_parser('add-role',
                                      help='Add a role!',
                                      description=__doc__)

    parser.add_argument('--use-local', action='store_true', default=False)
    parser.add_argument('-c', '--channel', action='append', default=[DEFAULT_CONTRIB_MODULE_CHANNEL])
    parser.add_argument('rolename')
    parser.add_argument('keys', nargs='*')
    parser.set_defaults(main=main)

