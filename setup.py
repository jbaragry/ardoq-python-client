"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ardoqpy',
    version='0.8.4',
    description='A python REST API wrapper for Ardoq - https://ardoq.com.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jbaragry/ardoq-python-client',
    author='Jason Baragry',
    author_email='jason.baragry@gmail.com',
    license='MIT',
    packages=['ardoqpy'],
    data_files=[('ardoqpy.cfg', ['ardoqpy/ardoqpy.cfg'])],
    classifiers=[
        'Development Status :: 3 - Alpha',
    # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],

    keywords='architecture ardoq REST API wrapper tool',
    install_requires=['cookiejar', 'configparser', 'requests'],
)
