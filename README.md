# pystx3
Python support for building and running a commerical product named Strategix/OneOffice

This repository contains a Python 3 package that enables a TAR archive (tarball) taken from the development
machine to be compiled from scratch without any previously compiled version of the product being available.

To build with this package using the sample tarball provided in the repository, perform the following steps:

1. Pull in the latest version of the package.
   $ git clone https://github.com/rpmoseley/pystx3.git
   $ cd pystx3

2. Ensure that the 'pdm' package manager is installed by executing the following command:
   $ ./bootstrap
