from twisted.internet import reactor

from plugin import Plugin
from utils import call


class Git(Plugin):
    """This plugin does not call git directly, instead it types the
    commands for you. This means that you have to be in a terminal
    window (xterm or whatever) before you press the pad on the
    launchpad.

    This plugin uses xvkbd to simulate keypresses so you need to have
    that installed (apt-get install xvkbd).

    Additionally, this plugin features a lock/unlock mechanism
    because: you have to unlock the plugin by pressing the unlock
    button, then you have 5 seconds to use the plugin's
    features. During these 5 seconds, the plugin pads flash
    orange. When the 5 second timeout passes, the pads go back to
    their usual color (red).
    """

    height = 1
    width = 5

    git_locked = True

    def setup(self):
        self._update_leds()

    def pad_down_callback(self, pad):
        if pad == 0:
            self._git('fetch gerrit')
        elif pad == 1:
            self._git('stash')
        elif pad == 2:
            self._git('rebase gerrit/master')
        elif pad == 3:
            self._git('push gerrit HEAD:refs/for/master')
        elif pad == 4:
            self._unlock()

    def _git(self, command):
        if self.git_locked:
            return

        call('xvkbd', '-text "git %s\\r"' % command)

    def _unlock(self):
        self.git_locked = False
        self._update_leds()
        reactor.callLater(5, self._lock)

    def _lock(self):
        self.git_locked = True
        self._update_leds()

    def _update_leds(self):
        """updates the leds based on the locked status"""
        if self.git_locked:
            self.launchpad.flash_off()
            color = self.launchpad.RED
        else:
            self.launchpad.flash_on()
            color = 0x3b

        for pad in range(self.width):
            self.launchpad.note_on(self.position + pad, color)
