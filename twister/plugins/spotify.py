from plugin import Plugin
from utils import call


class Spotify(Plugin):

    height = 1
    width = 3

    def pad_down_callback(self, pad):
        if pad == 0:
            self._send('Previous')
        elif pad == 1:
            self._send('PlayPause')
        elif pad == 2:
            self._send('Next')

    def _send(self, command):
        call('dbus-send', '--print-reply ' +
             '--dest=org.mpris.MediaPlayer2.spotify ' +
             '/org/mpris/MediaPlayer2 ' +
             'org.mpris.MediaPlayer2.Player.%s' % command)
