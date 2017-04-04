#!/usr/bin/env python

from os.path import join, dirname
from cloudify import ctx
ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA


def _delete_data():
    utils.sudo(['rm', '-rf', '/usr/pgsql-9.5'])


def _delete_logs():
    utils.sudo(['rm', '-rf', '/var/log/cloudify/postgresql'])


def main():
    _delete_data()
    _delete_logs()


main()
