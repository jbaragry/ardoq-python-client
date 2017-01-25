"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ardoqpy',
    version='0.0.1',
    description='A small REST API wratter in python for Ardoq - https://ardoq.com.',
    long_description=long_description,
    url='https://github.com/jbaragry/ardoq-python-client',
    author='Jason Baragry',
    license='MIT',
    packages=find_packages('ardoqpy'),
    package_dir={'': 'ardoqpy'},
    data_files=[('ardoqpy.cfg', ['ardoqpy/ardoqpy.cfg'])],
    classifiers=[
        'Development Status :: 3 - Alpha',
    # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Architecture',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='architecture ardoq REST API wrapper tool',
    install_requires=['cookiejar', 'configparser', 'Requests'],
)
