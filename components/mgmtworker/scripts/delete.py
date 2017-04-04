#!/usr/bin/env python

from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

runtime_props = ctx.instance.runtime_properties
node_props = ctx.node.properties


def _uninstall():
    mgmtworker_rpm = node_props['management_worker_rpm_source_url']
    utils.yum_remove(mgmtworker_rpm, ignore_failures=True)


def _delete_data():
    utils.remove(runtime_props['home_folder'])
    utils.remove(runtime_props['log_folder'])
    utils.remove_notice(runtime_props['service_name'])


def main():
    _uninstall()
    _delete_data()


main()
