#!/usr/bin/env python

from setuptools import setup, find_packages
from os.path import join, dirname

here = dirname(__file__)

setup(name='ftx',
      version='0.0.1',
      description="Unofficial python3 FTX exchange API 1.0.",
      long_description=open(join(here, 'README.md')).read(),
      license='MIT',
      author='thomgabriel',
      author_email='thomgabriel@protonmail.com',
      url='https://github.com/thomgabriel/ftx',
      download_url = 'https://github.com/thomgabriel/ftx/dist/ftx-0.0.1.tar.gz',
      install_requires=[
        'requests==2.23.0',
        'schedule==0.6.0',
        'satoshi==0.1.3'
      ],
      packages=find_packages(),
      keywords = ['ftx', 'bitcoin', 'crypto-api', 'api-connector', 'exchange-api',
      'crypto-exchange', 'digital-currency', 'trading'],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
      ],
      )

# PyPi publish flow
# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*