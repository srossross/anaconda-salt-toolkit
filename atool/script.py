'''
Anaconda Cloud command line manager
'''
from __future__ import print_function, unicode_literals

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
from os import makedirs
from os.path import join, exists, isfile

from atool import __version__ as version
from atool import commands as command_module

from clyent import add_default_arguments, add_subparser_modules
from clyent.logs import setup_logging
import sys


logger = logging.getLogger('atool')


def file_or_token(value):

    if isfile(value):
        with open(value) as fd:
            return fd.read().strip()
    if any(char in value for char in '/\\.'):
        # This chars will never be in a token value, but may be in a path
        # The error message will be handled by the parser
        raise ValueError()
    return value


def binstar_main(sub_command_module, args=None, exit=True, description=None, version=None, epilog=None):

    parser = ArgumentParser(description=description, epilog=epilog,
                            formatter_class=RawDescriptionHelpFormatter)

    add_default_arguments(parser, version)
    bgroup = parser.add_argument_group('anaconda-client options')
    bgroup.add_argument('-t', '--token', type=file_or_token,
                        help="Authentication token to use. "
                             "May be a token or a path to a file containing a token")
    bgroup.add_argument('-s', '--site',
                        help='select the anaconda-client site to use', default=None)

    add_subparser_modules(parser, sub_command_module, 'conda_server.subcommand')


    args = parser.parse_args(args)

    setup_logging(logger, args.log_level, use_color=args.color,
                  show_tb=args.show_traceback)

    if not hasattr(args, 'main'):
        parser.error("A sub command must be given. "
                     "To show all available sub commands, run:\n\n\t anaconda -h\n")
    return args.main(args)

def main(args=None, exit=True):
    binstar_main(command_module, args, exit,
                 description=__doc__, version=version)
