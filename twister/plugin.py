import ConfigParser
import importlib

from collections import namedtuple
from utils import camelcase

from utils import random_color


class Plugin(object):
    # height of the plugin in number of pads
    height = None

    # width of the plugin in number of pads
    width = None

    # a reference to the launchpad, set by launchpad when plugin is added to it
    launchpad = None

    def __init__(self, position, options):
        """Position is the position on the launchpad of the top-left
        pad of this plugin. Options is the list of (key, value) tuples
        from ConfigParser. Use the get_option method for convenient
        access to the options."""
        self.position = position
        self.options = options

    def setup(self):
        """Override this to run code at plugin startup, you can for
        example draw to the launchpad when this is called. This
        non-sense implementation just gives every pad that is in use a
        random color."""
        for pad in self.pads():
            self.launchpad.note_on(pad, random_color())

    def pad_down_callback(self, pad):
        """called when a pad is pressed, do nothing by default,
        override in plugin"""
        pass

    def pad_up_callback(self, pad):
        """called when a pad is released, do nothing by default,
        override in plugin"""
        pass

    def pads(self):
        """yields all of the pads this plugin uses, based on the
        width, height and position of the plugin"""
        for dx in range(self.width):
            for dy in range(self.height):
                yield self.position + dx + 0x10 * dy

    def get_option(self, option):
        """helper method to access elements of self.options which is a
        list of (key,value) tuples"""
        for key, value in self.options:
            if key == option:
                return value


def load_plugins(launchpad, configfile):
    """reads the configfile and adds the configured plugins to the
    launchpad"""
    parser = ConfigParser.SafeConfigParser()
    parser.read(configfile)

    for section in parser.sections():
            plugin = _parse_plugin(section, parser)
            launchpad.add_plugin(plugin)
            print("\t- %s" % section)


def _parse_plugin(section, parser):
    """parses a configfile section and returns an instance of the
    plugin"""

    # plugin defaults to section name if not explicitly specified
    if parser.has_option(section, 'plugin'):
        plugin_name = parser.get(section, 'plugin')
    else:
        plugin_name = section

    plugin_class = _get_plugin_class(plugin_name)

    # try position as base-10 or base-16
    position_str = parser.get(section, 'position')
    if position_str.startswith('0x'):
        position = int(position_str, 16)
    else:
        position = int(position_str)

    # instantiate plugin
    return plugin_class(position, parser.items(section))


def _get_plugin_class(plugin_name):
    """dynamically loads a plugin class

    Example: For a plugin named volume_manager a module named
    twister.plugins.volume_manager should exist and define a class
    named VolumeManager."""

    plugin_module = importlib.import_module(
        'plugins.%s' % plugin_name)
    plugin_class = getattr(plugin_module, camelcase(plugin_name))
    return plugin_class
