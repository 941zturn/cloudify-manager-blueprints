#!/usr/bin/env python

from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

runtime_props = ctx.instance.runtime_properties


@utils.retry(ValueError)
def check_worker_running():
    """Use `celery status` to check if the worker is running."""
    work_dir = join(runtime_props['home_dir'], 'work')
    celery_path = join(runtime_props['home_dir'], 'env', 'bin', 'celery')
    result = utils.sudo([
        'CELERY_WORK_DIR={0}'.format(work_dir),
        celery_path,
        '--config=cloudify.broker_config',
        'status'
    ], ignore_failures=True)
    if result.returncode != 0:
        raise ValueError('celery status: worker not running')


ctx.logger.info('Starting Management Worker Service...')
utils.start_service(runtime_props['service_name'])

utils.systemd.verify_alive(runtime_props['service_name'])

try:
    check_worker_running()
except ValueError:
    ctx.abort_operation('Celery worker failed to start')
