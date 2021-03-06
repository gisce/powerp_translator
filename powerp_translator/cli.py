from ooservice import OpenERPService, Transaction
from base64 import decodestring
from os.path import isdir
from os import makedirs, environ, listdir


import time
import logging
import osconf
import click
import sql_db


def createdb(dbname=False):
    conn = sql_db.db_connect('postgres')
    cursor = conn.cursor()
    if not dbname:
        dbname = 'translate_{}'.format(str(int(time.time())))
    try:
        cursor.autocommit(True)
        cursor.execute('CREATE DATABASE {}'.format(dbname))
        return dbname
    finally:
        cursor.close()
        sql_db.close_db('postgres')

def initialize_logger(verbosity):
    logging.basicConfig(
        format='[%(asctime)s](%(name)s) %(levelname)s: %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S',
        # Set custom level to avoid disabling from OpenERPService
        level=(verbosity + logging.CRITICAL) 
    )
    logger = logging.getLogger('TranslationExport')
    logger.addLevelName(logging.INFO + logging.CRITICAL, 'INFO')
    logger.addLevelName(logging.DEBUG + logging.CRITICAL, 'DEBUG')
    logger.addLevelName(logging.ERROR + logging.CRITICAL, 'ERROR')

def log_info(msg):
    logger = logging.getLogger('TranslationExport')
    logger.log(logging.INFO + logging.CRITICAL, msg)

def log_debug(msg):
    logger = logging.getLogger('TranslationExport')
    logger.log(logging.DEBUG + logging.CRITICAL, msg)

def log_error(msg):
    logger = logging.getLogger('TranslationExport')
    logger.log(logging.ERROR + logging.CRITICAL, msg)


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
    initialize_logger(verbosity)    
    log_info('Running with verbosity: {}'.format('DEBUG' if debug else 'INFO'))
    if modules:
        log_debug('Modules: {}'.format(modules))
    else:
        log_error('No Modules to export!')
        exit(-1)
    log_info('Starting OpenERP Service')
    log_debug('Checking for OpenERP env vars')
    dbname = 'translate_{}'.format(str(int(time.time())))
    try:
        confs = osconf.config_from_environment(
            'OPENERP',
            ['addons_path', 'root_path', 'db_user', 'db_password', 'db_name'],
            db_name=dbname
        )
    except:
        log_error(
            'Please, make sure you provide the following environment vars:'
            '\n\tOPENERP_ADDONS_PATH'
            '\n\tOPENERP_ROOT_PATH'
            '\n\tOPENERP_DB_USER'
            '\n\tOPENERP_DB_PASSWORD'
        )
        exit(-1)
    dbname = confs['db_name']
    environ['OPENERP_DB_NAME'] = dbname
    log_debug('DB_NAME: {}'.format(dbname))
    addons_path = confs['addons_path']
    log_debug('ADDONS_PATH: {}'.format(addons_path))
    root_path = confs['root_path']
    log_debug('ROOT_PATH: {}'.format(root_path))
    try:
        oerp_service = OpenERPService()
        log_info('Using database: {}'.format(dbname))
    except:
        log_info('Creating database: {}'.format(dbname))
        createdb(dbname=dbname)
        log_debug('Initialize OpenERPService')
        oerp_service = OpenERPService()
    for module_name in modules:
        log_info('Exporting module "{}"'.format(module_name))
        if module_name not in listdir(addons_path):
            log_error(
                'Module "{}" not found in addons path!'.format(module_name)
            )
            continue
        try:
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
                    print(
                        'More than one module found with this name: "{}"!'
                        ''.format(module_name))
                    module_id = module_id[0]
                if not len(module_id):
                    log_error('Module "{}" not found with this name'.format(
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
        except Exception as err:
            log_error(
                'Couldn\'t export translations for module "{}": {}'.format(
                    module_name, err
                )
            )
            continue
    log_info('Removing temp database {}'.format(dbname))
    oerp_service.drop_database()


if __name__ == '__main__':
    transexport()
