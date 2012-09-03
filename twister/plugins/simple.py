from plugin import Plugin
from utils import call


class Simple(Plugin):
    """Use this plugin if you just want to call some external utility
    when you press down on a pad."""

    height = 1
    width = 1

    def pad_down_callback(self, pad):
        call(self.get_option('executable'), self.get_option('arguments'))
