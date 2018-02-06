from ooservice import OpenERPService, Transaction
from base64 import decodestring
from os.path import isdir
from os import makedirs

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
    logger.debug('DB_NAME: {}'.format(dbname))
    addons_path = oerp_service.config['addons_path']
    logger.debug('ADDONS_PATH: {}'.format(addons_path))
    root_path = oerp_service.config['root_path']
    logger.debug('ROOT_PATH: {}'.format(root_path))
    try:
        for module_name in modules:
            logger.debug('Exporting module {}'.format(module_name))
            with Transaction().start(
                    database_name=dbname
            ) as temp:
                temp.service.install_module(module_name)
                uid = temp.user
                pool = temp.pool
                cursor = temp.cursor
                module_obj = pool.get('ir.module.module')
                export_wizard_obj = pool.get('wizard.module.lang.export')
                module_id = module_obj.search(cursor, uid, [
                    ('name', '=', module_name)
                ])
                if len(module_id) > 1:
                    logger.warn(
                        'More than one module found with this name: "{}"!'
                        ''.format(module_name))
                    module_id = module_id[0]
                if not len(module_id):
                    logger.error('Module "{}" not found with this name'.format(
                        module_name
                    ))
                    continue
                wizard_id = export_wizard_obj.create(cursor, uid, {
                    'format': 'po',
                    'modules': [(6, 0, module_id)]
                })
                wizard = export_wizard_obj.browse(cursor, uid, wizard_id)
                wizard.act_getfile()
                if not isdir(join(addons_path, module_name, 'i18n')):
                    makedirs(join(addons_path, module_name, 'i18n'))
                with open(
                    join(addons_path, module_name, 'i18n', module_name+'.pot'),
                    'w'
                ) as potfile:
                    potfile.write(decodestring(wizard.data))
                
    finally:
        oerp_service.drop_database()
        logger.debug('Removed temp database {}'.format(dbname))


if __name__ == '__main__':
    transexport()
