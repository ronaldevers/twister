from plugin import Plugin
from utils import call


class Xrandr(Plugin):

    height = 1
    width = 3

    def pad_down_callback(self, pad):
        if pad == 0:
            call('xrandr', '--auto')
        elif pad == 1:
            call('xrandr', '--output VGA-1 --left-of LVDS-1')
        elif pad == 2:
            call('xrandr', '--output VGA-1 --same-as LVDS-1')
