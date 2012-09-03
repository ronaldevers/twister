from plugin import Plugin
from utils import call


class AppRaiser(Plugin):
    height = 1
    width = 1

    def pad_down_callback(self, pad):
        window_class = self.get_option('window_class')
        call('wmctrl', '-xa %s' % window_class)
