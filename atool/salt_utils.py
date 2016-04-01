from __future__ import unicode_literals, print_function

import json
import logging
import sys
import time

import subprocess as sp
import yaml
import os

log = logging.getLogger('atool')


def run_command(command, fail_message, use_json=True):
    p0 = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    i = 0
    while p0.poll() is None:
        i += 1
        time.sleep(0.5)
        print('.' * (i % 4), '    ', end='\r')
        sys.stdout.flush()

    output = p0.stdout.read()
    if p0.returncode:
        print('...', 'FAIL')
        print(fail_message, '\n')
        print('    +', output.replace('\n', '\n    + '))
    else:
        print()
        log.debug(output)

    if use_json:
        return json.loads(output)

def handle_state_apply_result(results):
    for item in results.values():
        if item['result']:
            print('   ', item['comment'], 'OK')
        else:
            print('   ', item['comment'], 'FAILED')
            print(
                '    STDOUT:\n    +',
                item['changes']['stdout'].replace('\n', '\n    + ')
            )
            print(
                '    STDERR:\n    +',
                item['changes']['stderr'].replace('\n', '\n    + ')
            )

def enable_salt_state(rolename):
    salt_state_command = ['salt-call', '--out=json', '-l', 'quiet', '--local', 'state.apply', rolename]
    print("Enabling salt state {} from ...".format(rolename))
    log.debug(' '.join(salt_state_command))
    data = run_command(salt_state_command, 'Salt could not enable the role. Salt-call output::')
    handle_state_apply_result(data['local'])



def update_profile_pillar(rolename, profile_data):

    rolename = rolename.split('.')[0]

    profile_pillar = os.path.join(sys.exec_prefix, 'srv', 'pillar', 'profile', 'init.sls')
    if os.path.exists(profile_pillar):
        with open(profile_pillar, 'r') as fd:
            root = yaml.safe_load(fd)
    else:
        root = {}
    if root is None:
        root = {}

    data = root.setdefault('profile', {}).setdefault('data', {})
    data[rolename] = profile_data


    with open(profile_pillar, 'w') as fd:
        yaml.safe_dump(root, fd)
        log.debug("Updated File: {}".format(profile_pillar))


def update_roles_pillar(rolename, profile_data):

    rolename = rolename.split('.')[0]

    role_pillar = os.path.join(sys.exec_prefix, 'srv', 'pillar', 'roles', 'init.sls')

    if not os.path.exists(os.path.dirname(role_pillar)):
        os.makedirs(os.path.dirname(role_pillar))

    if os.path.exists(role_pillar):
        with open(role_pillar, 'r') as fd:
            root = yaml.safe_load(fd)
    else:
        root = {}

    if root is None:
        root = {}

    roles = root.setdefault('roles', [])
    roles.append(rolename)
    root['roles'] = list(set(roles))


    with open(role_pillar, 'w') as fd:
        yaml.safe_dump(root, fd)
        log.debug("Updated File: {}".format(role_pillar))



