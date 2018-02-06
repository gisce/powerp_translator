from setuptools import setup, find_packages


setup(
    name='powerp_translator',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/gisce/destral',
    install_requires=[
        'osconf',
        'click',
        'python-dateutil',
        'mamba',
        'coverage',
        'babel>=2.4.0',
        'ooservice'
    ],
    entry_points={
        'console_scripts': [
            'transexport = powerp_translator.cli:transexport'
        ]
    },
    license='GNU GPLv3',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='OpenERP external translation framework'
)
