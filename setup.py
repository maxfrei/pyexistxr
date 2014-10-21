#!/usr/bin/env python
from distutils.core import setup


setup(name="pyexistxr",
      version="0.01",
      description="eXist database proxy via XML-RPC",
      author="Sviridov Alexey",
      author_email="sviridov84@gmail.com",
      url="https://github.com/maxfrei/pyexistxr",
      package_dir={'pyexistxr': ''},
      packages=['pyexistxr'],
      license = "GPL-2",
      classifiers=(
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          )
      )
