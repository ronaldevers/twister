import os
import random
import re
import shlex

from twisted.internet import utils

from launchpad import Launchpad


def camelcase(string):
    """convert a string from under_score to CamelCase"""
    result = []
    for token in string.split('_'):
        result.append(token[0].upper() + token[1:])
    return "".join(result)


def underscore(string):
    """convert a string from CamelCase to under_score"""
    return re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', string).lower().strip('_')


def print_exit_code(exit_code):
    print "exit code", exit_code


def call(executable, args=None, path=None):
    """call an external process in a separate thread, when the process
    returns, print the exit-code

    returns the deferred"""
    print 'Calling', executable, args

    if args:
        args = shlex.split(str(args))
        d = utils.getProcessOutput(executable, args=args, env=os.environ, path=path)
    else:
        d = utils.getProcessOutput(executable, env=os.environ, path=path)

    d.addCallback(print_exit_code)
    return d


def random_color():
    """returns red, green or amber, encoded in the format understood
    by the launchpad"""
    red = random.random() > .5
    green = random.random() > .5

    if not red and not green:
        return random_color()

    return (Launchpad.RED * red) | (Launchpad.GREEN * green)
