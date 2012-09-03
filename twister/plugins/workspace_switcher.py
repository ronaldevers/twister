from plugin import Plugin
from utils import call


class WorkspaceSwitcher(Plugin):

    height = 2
    width = 2

    def pad_down_callback(self, pad):
        if pad == 0 or pad == 1:
            self._switch_to(pad)
        elif pad == 0x10 or pad == 0x11:
            self._switch_to(pad - 0x10 + 2)

    def _switch_to(self, workspace):
        call('wmctrl', '-s %d' % workspace)

    # workspace switching
    # 0x60: lambda _: call('/usr/bin/wmctrl', '-s 0'),
    # 0x61: lambda _: call('/usr/bin/wmctrl', '-s 1'),
    # 0x70: lambda _: call('/usr/bin/wmctrl', '-s 2'),
    # 0x71: lambda _: call('/usr/bin/wmctrl', '-s 3'),
