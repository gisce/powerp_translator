import logging
import click

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True))
@click.option('--modules', '-m', multiple=True)
@click.option('--verbose', '-v', type=click.BOOL, default=False, is_flag=True)
@click.option('--debug', '-d', type=click.BOOL, default=False, is_flag=True)
def transexport(modules=[], verbose=False, debug=False):
    verbosity = logging.DEBUG if debug else (
        logging.INFO if verbose else logging.WARNING)
    logging.basicConfig(
        format='[%(asctime)s](%(name)s) %(levelname)s: %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S',
        level=verbosity
    )
    logger = logging.getLogger('transexport')
    logger.info('Running with verbosity: {}'.format('DEBUG' if debug else 'INFO'))


if __name__ == '__main__':
    transexport()
