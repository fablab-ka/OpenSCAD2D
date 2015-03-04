# -*- coding: UTF-8 -*-
# pylint: skip-file
import sys
from distutils.core import setup
from setuptools import find_packages
import py2exe


with open('src/__pkginfo__.py') as f:
    exec(f.read())
_VERSION = globals()['__version__']

if sys.version_info < (2, 7):
    raise Exception('OpenSCAD2D %s requires Python 2.6 or higher.' % _VERSION)


_PACKAGES = find_packages(exclude=["*.test", "*.test.*", "test.*", "test"])

_INSTALL_REQUIRES = [
    'pylint>=1.4',
    'pylint-plugin-utils>=0.2.3',
    'pylint-common>=0.2.1',
    'requirements-detector>=0.3',
    'setoptconf>=0.2.0',
    'pyparsing==2.0.3',
    'pywatch==0.4',
    'shapely',
    'svgwrite',
]

_PACKAGE_DATA = {
    'src': [
        # todo include samples
    ]
}

_CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'GNU General Public License v2 or later (GPLv2+)',
)

_OPTIONAL = {
}
_OPTIONAL['with_everything'] = [req for req_list in _OPTIONAL.values() for req in req_list]


setup(
    name='OpenSCAD2D',
    version=_VERSION,
    url='https://github.com/fablab-ka/OpenSCAD2D',
    author='Sven Hecht',
    author_email='sven@fablab-karlsruhe.de',
    license='GPLv2',
    zip_safe=False,
    description='OpenSCAD2D is a script-based 2D CAD Modeller',
    keywords='openscad 2d cad lasercutter design',
    classifiers=_CLASSIFIERS,
    package_data=_PACKAGE_DATA,
    include_package_data=True,
    packages=_PACKAGES,
    entry_points={
        'console_scripts': [
            'openscad = openscad.run:main',
        ],
    },
    install_requires=_INSTALL_REQUIRES,
    extras_require=_OPTIONAL,
    #options={"py2exe": {"skip_archive": True, "includes": ["PyQt4.QtCore", "PyQt4.QtGui"]}},
    console=["src/openscad2d.py"]
)