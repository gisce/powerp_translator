from setuptools import setup, find_packages


setup(
    name='powerp-translator',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/gisce/destral',
    install_requires=[
        'osconf',
        'python-dateutil'
        'mamba',
        'coverage',
        'babel>=2.4.0'
    ],
    license='GNU GPLv3',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='OpenERP external translation framework'
)
