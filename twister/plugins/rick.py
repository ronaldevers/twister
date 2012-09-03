from plugin import Plugin
from utils import call


class Rick(Plugin):

    height = 1
    width = 1

    def pad_down_callback(self, pad):
        call('rick')

    def pad_up_callback(self, pad):
        call('killall', 'mpg123')

