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


def enable_salt_state(rolename):
    salt_state_command = ['salt-call', '--out=json', '-l', 'quiet', '--local', 'state.sls', rolename]
    print("Enabling salt state {} from ...".format(rolename))
    log.debug(' '.join(salt_state_command))
    data = run_command(salt_state_command, 'Salt could not enable the role. Salt-call output::')
    print(data)


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


def update_profile_grain(rolename, profile_data):

    rolename = rolename.split('.')[0]

    profile_grain = os.path.join(sys.exec_prefix, 'srv', 'pillar', 'profile', 'init.sls')
    if os.path.exists(profile_grain):
        with open(profile_grain, 'r') as fd:
            root = yaml.safe_load(fd)
    else:
        root = {}
    if root is None:
        root = {}

    data = root.setdefault('profile', {}).setdefault('data', {})
    data[rolename] = profile_data


    with open(profile_grain, 'w') as fd:
        yaml.safe_dump(root, fd)
        log.debug("Updated File: {}".format(profile_grain))


def update_roles_grain(rolename, profile_data):

    rolename = rolename.split('.')[0]

    role_grain = os.path.join(sys.exec_prefix, 'srv', 'pillar', 'roles', 'init.sls')
    
    if not os.path.exists(os.path.dirname(role_grain)):
        os.makedirs(os.path.dirname(role_grain))

    if os.path.exists(role_grain):
        with open(role_grain, 'r') as fd:
            root = yaml.safe_load(fd)
    else:
        root = {}

    if root is None:
        root = {}

    roles = root.setdefault('roles', [])
    roles.append(rolename)
    root['roles'] = list(set(roles))


    with open(role_grain, 'w') as fd:
        yaml.safe_dump(root, fd)
        log.debug("Updated File: {}".format(role_grain))





def main(args):
    print("Adding Role", args.rolename)

    profile_data = get_profile_data(args.keys)
    install_conda_salt_module(args.rolename, args.use_local, args.channel)
    update_profile_grain(args.rolename, profile_data)
    enable_salt_state(args.rolename)

    update_roles_grain(args.rolename, profile_data)




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

