#!/usr/bin/python

import argparse
import sys

from twisted.internet import reactor

from launchpad import Launchpad
from plugin import load_plugins


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configfile',
                        help='read midi mappings from this file, '
                        'defaults to ~/.twister.conf',
                        default='~/.twister.conf')
    parser.add_argument('-p', '--port',
                        type=int,
                        help='the midi port to open, '
                        'use arecordmidi -l to get a list (remove ":0" from port)')
    return parser.parse_args()


class Twister(object):

    def __init__(self):
        args = _parse_args()

        if not args.port:
            print("ERROR: Please use -p option to specify device midi port.")
            sys.exit(1)

        # connect with the launchpad
        print("Connecting with launchpad")
        self.launchpad = Launchpad(args.port, self.process_midi_event)

        # load the plugins
        print("Loading plugins using config file: %s" % args.configfile)
        load_plugins(self.launchpad, args.configfile)

        # start reading midi events
        self.launchpad.read_midi_event()


    def process_midi_event(self, data):
        if data is None:
            return

        # for note events there is note and velocity,
        # for control events those are called param and value
        #   in alsa, but we just call them note and velocity also
        midi_type, channel, note, velocity = data

        plugin = self.launchpad.get_plugin(note)
        if not plugin:
            return

        # figure out which callback to call
        if midi_type == Launchpad.TYPE_NOTEON and velocity == 0:
            plugin.pad_up_callback(note - plugin.position)
        elif midi_type == Launchpad.TYPE_NOTEON:
            plugin.pad_down_callback(note - plugin.position)
        elif midi_type == Launchpad.TYPE_CONTROL:
            launchpad.shutdown()
            reactor.shutdown()


if __name__ == '__main__':
    twister = Twister()
    reactor.run()
