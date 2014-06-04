#!/usr/bin/env python

from setuptools import setup


setup(
    name='APRS-MS',
    version='0.1',
    description='An email interface to APRS messaging',
    license='BSD',
    author='Antony Chazapis',
    author_email='chazapis@gmail.com',
    url='https://github.com/chazapis/APRS-MS',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Ham Radio'
    ],
    keywords='ham radio, APRS, email',
    install_requires=['SQLALchemy >= 0.9', 'Twisted >= 13.2', 'zope.interface >= 3.8'],
    packages=['aprs_ms'],
    zip_safe=False,
    entry_points={'console_scripts': ['aprs-ms-collect = aprs_ms.collect:main',
                                      'aprs-ms-imap = aprs_ms.imap:main']},
)
