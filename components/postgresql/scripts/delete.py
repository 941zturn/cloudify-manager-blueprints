#!/usr/bin/env python

from os.path import join, dirname
from cloudify import ctx
ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA


def _remove_service():
    service_name = ctx.instance.runtime_properties['service_name']
    try:
        ctx.logger.debug('Stopping service: {0}'.format(service_name))
        utils.systemd.stop(service_name)
    except RuntimeError:
        pass
    try:
        ctx.logger.debug('Disabling service: {0}'.format(service_name))
        utils.systemd.disable(service_name)
    except RuntimeError:
        pass
    try:
        ctx.logger.debug('Removing service: {0}'.format(service_name))
        utils.systemd.remove(service_name)
    except RuntimeError:
        pass


def _uninstall_pgsql():
    packages_to_remove = ['postgresql95', 'postgresql95-libs']  # + \
    #  ctx.instance.runtime_properties['installed_packages']
    for package in packages_to_remove:
        ctx.logger.debug('Removing package: {0}'.format(package))
        utils.yum_remove(package, ignore_failures=True)


def _delete_data():
    paths_to_remove = ['/opt/cloudify/postgresql',
                       '/opt/cloudify/postgresql-9.5',
                       '/var/lib/pgsql',
                       '/usr/pgsql-9.5']
    for path in paths_to_remove:
        ctx.logger.debug('Deleting path: {0}'.format(path))
        utils.remove(path)


def _delete_logs():
    path = ctx.instance.runtime_properties['logs_path']
    utils.remove(path)


def _delete_notice():
    service_name = ctx.instance.runtime_properties['components_folder']
    utils.remove_notice(service_name)


def main():
    _remove_service()
    _uninstall_pgsql()
    _delete_data()
    _delete_logs()
    _delete_notice()


main()
