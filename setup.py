"""
    scratchdir
    ~~~~~~~~~~

    Context manager used to maintain your temporary directories/files.

    :copyright: (c) 2017 Andrew Hawker.
    :license: Apache 2.0, see LICENSE for more details.
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='scratchdir',
    version='0.0.1',
    author='Andrew Hawker',
    author_email='andrew.r.hawker@gmail.com',
    url='https://github.com/ahawker/scratchdir',
    license='Apache 2.0',
    description='Context manager used to maintain your temporary directories/files.',
    long_description=__doc__,
    py_modules=['scratchdir'],
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    )
)
