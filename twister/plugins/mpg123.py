from plugin import Plugin
from utils import call


class Mpg123(Plugin):
    """Plays mp3's in a subprocess using mpg123. Press button once to
    start off the mp3, press button again to kill all mpg123's
    running.

    Example config:

    [rickroll]
    mp3 = /path/to/rick.mp3
    plugin = mpg123
    position = 0"""

    height = 1
    width = 1
    playing = False

    def pad_down_callback(self, pad):
        # TODO use the deferred to blink the led on start and stop
        #      blinking when playback has finished
        if not self.playing:
            self.start()
        else:
            self.stop()

        self.playing = not self.playing


    def start(self):
        call('mpg123', self.get_option('mp3'))

    def stop(self):
        call('killall', 'mpg123')
