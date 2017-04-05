#!/usr/bin/env python

from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

runtime_props = ctx.instance.runtime_properties


def _uninstall():
    utils.yum_remove(runtime_props['service_name'], ignore_failures=True)


def _delete_data():
    utils.remove(runtime_props['log_dir'])
    utils.remove_notice(runtime_props['service_name'])


def main():
    _uninstall()
    _delete_data()


main()
