# -*- encoding: utf-8 -*-
#
# nettest.py
# ----------
# In here is the NetTest API definition. This is how people
# interested in writing ooniprobe tests will be specifying them
#
# :authors: Arturo Filastò, Isis Lovecruft
# :license: see included LICENSE file

import sys
import os
import itertools
import traceback

from twisted.trial import unittest, itrial, util
from twisted.internet import defer, utils
from twisted.python import usage

from ooni.utils import log

class NetTestCase(object):
    """
    This is the base of the OONI nettest universe. When you write a nettest
    you will subclass this object.

    * inputs: can be set to a static set of inputs. All the tests (the methods
      starting with the "test" prefix) will be run once per input.  At every run
      the _input_ attribute of the TestCase instance will be set to the value of
      the current iteration over inputs.  Any python iterable object can be set
      to inputs.

    * inputFile: attribute should be set to an array containing the command line
      argument that should be used as the input file. Such array looks like
      this:

          ``["commandlinearg", "c", "default value" "The description"]``

      The second value of such arrray is the shorthand for the command line arg.
      The user will then be able to specify inputs to the test via:

          ``ooniprobe mytest.py --commandlinearg path/to/file.txt``

      or

          ``ooniprobe mytest.py -c path/to/file.txt``


    * inputProcessor: should be set to a function that takes as argument a
      filename and it will return the input to be passed to the test
      instance.

    * name: should be set to the name of the test.

    * author: should contain the name and contact details for the test author.
      The format for such string is as follows:

          ``The Name <email@example.com>``

    * version: is the version string of the test.

    * requiresRoot: set to True if the test must be run as root.

    * usageOptions: a subclass of twisted.python.usage.Options for processing of command line arguments

    * localOptions: contains the parsed command line arguments.

    Quirks:
    Every class that is prefixed with test *must* return a twisted.internet.defer.Deferred.
    """
    name = "I Did Not Change The Name"
    author = "Jane Doe <foo@example.com>"
    version = "0.0.0"

    inputs = [None]
    inputFile = None

    report = {}
    report['errors'] = []

    usageOptions = None

    optParameters = None

    requiredOptions = []
    requiresRoot = False

    localOptions = {}
    def _setUp(self):
        """
        This is the internal setup method to be overwritten by templates.
        """
        pass

    def setUp(self):
        """
        Place here your logic to be executed when the test is being setup.
        """
        pass

    def inputProcessor(self, filename=None):
        """
        You may replace this with your own custom input processor. It takes as
        input a file descriptor so remember to close it when you are done.

        This can be useful when you have some input data that is in a certain
        format and you want to set the input attribute of the test to something
        that you will be able to properly process.

        For example you may wish to have an input processor that will allow you
        to ignore comments in files. This can be easily achieved like so:

            fp = open(filename)
            for x in fp.xreadlines():
                if x.startswith("#"):
                    continue
                yield x.strip()
            fp.close()

        Other fun stuff is also possible.
        """
        log.debug("Running default input processor")
        if filename:
            fp = open(filename)
            for x in fp.xreadlines():
                yield x.strip()
            fp.close()
        else:
            pass

    def _checkRequiredOptions(self):
        for required_option in self.requiredOptions:
            log.debug("Checking if %s is present" % required_option)
            if not self.localOptions[required_option]:
                raise usage.UsageError("%s not specified!" % required_option)

    def _processOptions(self, options=None):
        if self.inputFile:
            self.inputs = self.inputProcessor(self.inputFile)

        self._checkRequiredOptions()

        # XXX perhaps we may want to name and version to be inside of a
        # different method that is not called options.
        return {'inputs': self.inputs,
                'name': self.name,
                'version': self.version}

    def __repr__(self):
        return "<%s inputs=%s>" % (self.__class__, self.inputs)

