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
    utils.systemd.remove(runtime_props['service_name'])

    rest_service_package = node_props['rest_service_rpm_source_url']
    utils.yum_remove(rest_service_package, ignore_failures=True)


def _delete_data():
    utils.remove(runtime_props['home_dir'])  # /opt/manager
    utils.remove(runtime_props['log_dir'])
    utils.remove_notice(runtime_props['service_name'])
    utils.remove_logrotate(runtime_props['service_name'])


def main():
    _uninstall()
    _delete_data()


main()
