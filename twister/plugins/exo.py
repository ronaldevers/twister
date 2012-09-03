from plugin import Plugin
from utils import call


class Exo(Plugin):
    height = 1
    width = 1

    def pad_down_callback(self, pad):
        call('exo-open', self.get_option('uri'))
