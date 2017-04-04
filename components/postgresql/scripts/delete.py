#!/usr/bin/env python

from os.path import join, dirname
from cloudify import ctx
ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA


def _uninstall_pgsql():
    packages_to_remove = ['postgresql95', 'postgresql95-libs']
    paths_to_remove = ['/opt/cloudify/postgresql',
                       '/opt/cloudify/postgresql-9.5',
                       '/usr/pgsql-9.5']
    for package in packages_to_remove:
        utils.yum_remove(package, ignore_failures=True)
    for path in paths_to_remove:
        utils.remove(path)


def _delete_logs():
    path = ctx.instance.runtime_properties['logs_path']
    utils.remove(path)


def _delete_notice():
    service_name = ctx.instance.runtime_properties['components_folder']
    utils.remove_notice(service_name)


def main():
    _uninstall_pgsql()
    _delete_logs()
    _delete_notice()


main()
