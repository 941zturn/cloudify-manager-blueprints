#!/usr/bin/env python

import os
from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

# Some runtime properties to be used in teardown
runtime_props = ctx.instance.runtime_properties
runtime_props['service_name'] = 'java'
runtime_props['log_dir'] = join(utils.BASE_LOG_DIR,
                                runtime_props['service_name'])

ctx_properties = utils.ctx_factory.create(runtime_props['service_name'])


def install_java():
    java_source_url = ctx_properties['java_rpm_source_url']

    ctx.logger.info('Installing Java...')
    utils.set_selinux_permissive()
    utils.copy_notice(runtime_props['service_name'])

    utils.yum_install(java_source_url, runtime_props['service_name'])

    utils.mkdir(runtime_props['log_dir'])

    # Java install log is dropped in /var/log.
    # Move it to live with the rest of the cloudify logs
    java_install_log = '/var/log/java_install.log'
    if os.path.isfile(java_install_log):
        utils.move(java_install_log, runtime_props['log_dir'])


install_java()
