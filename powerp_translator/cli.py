from ooservice import OpenERPService, Transaction

import time
import logging
import osconf
import click

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True))
@click.option(
    '--modules', '-m', multiple=True, help='Modules to export translations')
@click.option(
    '--verbose', '-v', type=click.BOOL, default=False, is_flag=True,
    help='Set Logger level to INFO')
@click.option(
    '--debug', '-d', type=click.BOOL, default=False, is_flag=True,
    help='Set Logger level to DEBUG. DEBUG level includes INFO level')
def transexport(modules=[], verbose=False, debug=False):
    verbosity = logging.DEBUG if debug else (
        logging.INFO if verbose else logging.WARNING)
    logging.basicConfig(
        format='[%(asctime)s](%(name)s) %(levelname)s: %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S',
        level=verbosity
    )
    logger = logging.getLogger('TranslationExport')
    logger.info('Running with verbosity: {}'.format('DEBUG' if debug else 'INFO'))
    if modules:
        logger.debug('Modules: {}'.format(modules))
    else:
        logger.error('No Modules to export!')
        exit(-1)
    logger.info('Starting OpenERP Service')
    logger.debug('Checking for OpenERP env vars')
    osconf.config_from_environment(
        'OPENERP',
        ['addons_path', 'root_path', 'db_user', 'db_password', 'db_name'],
        db_name='translate_{}'.format(time.time())
    )
    oerp_service = OpenERPService()
    dbname = oerp_service.db_name
    addons_path = oerp_service.config['addons_path']
    root_path = oerp_service.config['root_path']
    try:
        for module_name in modules:
            logger.debug('Testing module {}'.format(module_name))
            with Transaction().start(
                    database_name=dbname
            ) as temp:
                temp.service.install_module(module_name)
                pass
    finally:
        oerp_service.drop_database()


if __name__ == '__main__':
    transexport()
