from launchpad import Launchpad
from plugin import Plugin
from utils import call

GREEN = Launchpad.GREEN
YELLOW = Launchpad.YELLOW
ORANGE = Launchpad.ORANGE
RED = Launchpad.RED

# the round pad at the end of the row is the mute pad
MUTE_PAD = 8

class Volume(Plugin):
    height = 1
    width = 9

    # "sane" defaults
    volume = 7
    muted = False

    # map from 0-7 pad volume range to ALSA's 0-64 volume range
    volume_map = {0:  5,
                  1: 10,
                  2: 15,
                  3: 20,
                  4: 30,
                  5: 40,
                  6: 50,
                  7: 64}

    # map from volume to color
    color_map = {0: GREEN,
                 1: GREEN,
                 2: GREEN,
                 3: GREEN,
                 4: ORANGE,
                 5: ORANGE,
                 6: RED,
                 7: RED}

    def setup(self):
        # position + 8 is the round mute button
        self.launchpad.note_on(self.position + MUTE_PAD, GREEN)
        self._update_leds()

    def pad_down_callback(self, pad):
        if pad == MUTE_PAD:
            return self._toggle_mute()
        else:
            return self._set_volume(pad)

    def _toggle_mute(self):
        if self.muted:
            call('amixer', '-c 0 set Master unmute')
            self.launchpad.note_on(self.position + MUTE_PAD, GREEN)
        else:
            call('amixer', '-c 0 set Master mute')
            self.launchpad.note_on(self.position + MUTE_PAD, RED)

        self.muted = not self.muted

        # use 0 to force redrawing
        self._update_leds()

    def _set_volume(self, volume):
        # remember
        old_volume = self.volume
        self.volume = volume

        # actually set the volume
        call('/usr/bin/amixer', '-c 0 set Master %s' % self.volume_map[volume])

        # sync the LEDs
        self._update_leds(volume, old_volume)

    def _update_leds(self, volume=None, old_volume=None):
        # for shading the LEDs if sound is muted
        mask = 0x1d if self.muted else 0xff

        # start 'from scratch' if we don't know the old volume
        if old_volume is None:
            self._clear()
            old_volume = -1

        # use current volume if none was provided
        if volume is None:
            volume = self.volume

        if volume > old_volume:
            # volume was raised
            #
            # if we go from 4 to 6 then we want to turn on 5 and 6
            for v in range(old_volume + 1, volume + 1):
                self.launchpad.note_on(self.position + v, self.color_map[v] & mask)
        elif volume < old_volume:
            # volume was lowered
            #
            # if we go from 6 to 4 then we want to turn off 5 and 6
            for v in range(volume + 1, old_volume + 1):
                self.launchpad.note_off(self.position + v)

    def _clear(self):
        """turn off all leds, using CLEAR to clear both buffers (see
        double buffering section in launchpad programming guide)"""
        for pad in range(self.width - 1):
            self.launchpad.note_off(self.position + pad)
