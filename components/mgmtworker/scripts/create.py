#!/usr/bin/env python

from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA


# Some runtime properties to be used in teardown
runtime_props = ctx.instance.runtime_properties
runtime_props['service_name'] = 'mgmtworker'
runtime_props['home_dir'] = '/opt/mgmtworker'
runtime_props['log_dir'] = '/var/log/cloudify/mgmtworker'

ctx_properties = utils.ctx_factory.create(runtime_props['service_name'])


def _install_optional():
    mgmtworker_venv = '{0}/env'.format(runtime_props['home_dir'])
    rest_props = utils.ctx_factory.get('restservice')
    rest_client_source_url = \
        rest_props['rest_client_module_source_url']
    plugins_common_source_url = \
        rest_props['plugins_common_module_source_url']
    script_plugin_source_url = \
        rest_props['script_plugin_module_source_url']
    rest_service_source_url = \
        rest_props['rest_service_module_source_url']
    agent_source_url = \
        rest_props['agent_module_source_url']

    # this allows to upgrade modules if necessary.
    ctx.logger.info('Installing Optional Packages if supplied...')
    if rest_client_source_url:
        utils.install_python_package(rest_client_source_url, mgmtworker_venv)
    if plugins_common_source_url:
        utils.install_python_package(
            plugins_common_source_url, mgmtworker_venv)
    if script_plugin_source_url:
        utils.install_python_package(script_plugin_source_url, mgmtworker_venv)
    if agent_source_url:
        utils.install_python_package(agent_source_url, mgmtworker_venv)

    if rest_service_source_url:
        ctx.logger.info('Downloading cloudify-manager Repository...')
        manager_repo = \
            utils.download_cloudify_resource(rest_service_source_url,
                                             runtime_props['service_name'])
        ctx.logger.info('Extracting Manager Repository...')
        utils.untar(manager_repo)

        ctx.logger.info('Installing Management Worker Plugins...')
        # shouldn't we extract the riemann-controller and workflows modules to
        # their own repos?
        utils.install_python_package(
            '/tmp/plugins/riemann-controller', mgmtworker_venv)
        utils.install_python_package('/tmp/workflows', mgmtworker_venv)


def install_mgmtworker():

    management_worker_rpm_source_url = \
        ctx_properties['management_worker_rpm_source_url']

    runtime_props['rabbitmq_endpoint_ip'] = utils.get_rabbitmq_endpoint_ip()

    # Fix possible injections in json of rabbit credentials
    # See json.org for string spec
    for key in ['rabbitmq_username', 'rabbitmq_password']:
        # We will not escape newlines or other control characters,
        # we will accept them breaking
        # things noisily, e.g. on newlines and backspaces.
        # TODO: add:
        # sed 's/"/\\"/' | sed 's/\\/\\\\/' | sed s-/-\\/- | sed 's/\t/\\t/'
        runtime_props[key] = ctx_properties[key]

    runtime_props['rabbitmq_ssl_enabled'] = True

    ctx.logger.info('Installing Management Worker...')
    utils.set_selinux_permissive()

    utils.copy_notice(runtime_props['service_name'])
    utils.mkdir(runtime_props['home_dir'])
    utils.mkdir('{0}/config'.format(runtime_props['home_dir']))
    utils.mkdir('{0}/work'.format(runtime_props['home_dir']))
    utils.mkdir(runtime_props['log_dir'])

    # this create the mgmtworker_venv and installs the relevant
    # modules into it.
    utils.yum_install(management_worker_rpm_source_url,
                      service_name=runtime_props['home_dir'])
    _install_optional()

    # Add certificate and select port, as applicable
    runtime_props['broker_cert_path'] = utils.INTERNAL_CERT_PATH
    # Use SSL port
    runtime_props['broker_port'] = '5671'

    ctx.logger.info("broker_port: {0}".format(runtime_props['broker_port']))


install_mgmtworker()
