from launchpad import Launchpad
from plugin import Plugin
from utils import call

GREEN = Launchpad.GREEN
YELLOW = Launchpad.YELLOW
ORANGE = Launchpad.ORANGE
RED = Launchpad.RED


class Volume(Plugin):
    height = 1
    width = 9
    volume = 3

    volume_map = {0:  5,
                  1: 10,
                  2: 15,
                  3: 20,
                  4: 30,
                  5: 40,
                  6: 50,
                  7: 64}

    def pad_down_callback(self, pad):
        if pad == 8:
            return self._toggle_mute()
        else:
            return self._set_volume(pad)

    def _toggle_mute(self):
        call('amixer', '-c 0 set Master toggle')
        self._set_leds(mask=0x1d)

    def _set_volume(self, volume):
        # remember
        self.volume = volume

        # actually set the volume
        call('/usr/bin/amixer', '-c 0 set Master %s' % self.volume_map[volume])

        # sync the LEDs
        self._set_leds()

    def _set_leds(self, mask=0xff):
        self._clear()
        if self.volume >= 0: self.launchpad.note_on(self.position + 0, GREEN & mask)
        if self.volume >= 1: self.launchpad.note_on(self.position + 1, GREEN & mask)
        if self.volume >= 2: self.launchpad.note_on(self.position + 2, GREEN & mask)
        if self.volume >= 3: self.launchpad.note_on(self.position + 3, GREEN & mask)
        if self.volume >= 4: self.launchpad.note_on(self.position + 4, ORANGE & mask)
        if self.volume >= 5: self.launchpad.note_on(self.position + 5, ORANGE & mask)
        if self.volume >= 6: self.launchpad.note_on(self.position + 6, RED & mask)
        if self.volume == 7: self.launchpad.note_on(self.position + 7, RED & mask)

    def _clear(self):
        """turn off all leds, using CLEAR to clear both buffers (see
        double buffering section in launchpad programming guide)"""
        for pad in range(width):
            self.launchpad.note_on(self.position + pad, self.launchpad.CLEAR)
