# pystx3
Python support for building and running a commerical product named Strategix/OneOffice

This repository contains a Python 3 package that enables a TAR archive (tarball) taken from the development
machine to be compiled from scratch without any previously compiled version of the product being available.

The package is expected to be used within a virtual environment so that any dependant libraries can be
installed without impacting the rest of the system, it makes use of APSW for the independant database
support, and also SCONS as the build system. 

To build with this package using the sample tarball provided in the repository, perform the following steps:

1. Create new virtual enviornment to contain the package and its dependants:
   $ python3.7 -m venv ~/virtenv/PyStx3
   $ source ~/virtenv/PyStx3/bin/activate
   $ cd $VIRTUAL_ENV
   
2. Pull in the latest version of the package and submodules:
   $ git clone https://github.com/rpmoseley/pystx3.git
   
3. Pull out the dependant submodules required by the package:
   $ git submodule update --init
