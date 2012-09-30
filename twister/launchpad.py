import midirwp


class Launchpad(object):
    """Interface to the Novation Launchpad device."""

    # to stop doing blocking reads during shutdown
    stop = False

    # midi message types
    #
    # the launchpad sends note messages for the 8x8 grid and the
    # buttons on the right of it and it sends control messages for the
    # top row of pads
    #
    # the velocity or value is 127 for a pad-down, and 0 for a pad-up
    # event
    TYPE_NOTEON = 0x6
    TYPE_CONTROL = 0xa

    # velocities or values to send to the device to control the LEDs
    RED = 0x0f
    GREEN = 0x3c
    YELLOW = 0x3e
    ORANGE = 0x3f

    # Use this flag (in velocity/color/value) if you want to clear the
    # 'updating' buffer. So to completely turn off a LED, in both the
    # update and the display buffer, use a 'color' of precisely CLEAR.
    CLEAR = 0x8

    # Use this flag to copy the display value to the update buffer.
    COPY = 0x4

    # the launchpad sends and receives messages on channel 0
    CHANNEL = 0

    def __init__(self, port, midi_callback):
        """connects with the device using the midirwp ALSA module"""
        midirwp.setup(port)
        self.reset()
        self.midi_callback = midi_callback
        self.plugin_map = {}


    #
    # MIDI WRITING
    #


    def note_on(self, note, color, flash=False):
        """Sends a note-on message to the device to control the LEDs
        under a pad.

        The pads are numbered from 0 to 8 on the first row (with
        square pads), 0x10 to 0x18 on the second row and so on. The
        top row of round pads is numbered from 0x68 to 0x6f."""
        color = self._flashify(color, flash)
        midirwp.send_note_on(self.CHANNEL, note, color)

    def note_off(self, note):
        """turn off the LEDs under a pad"""
        midirwp.send_note_on(self.CHANNEL, note, self.CLEAR)

    def control_on(self, param, color, flash=False):
        """turn on the LEDs under a pad in the top row

        The top row is controlled using control messages instead of
        note-on messages."""
        color = self._flashify(color, flash)
        midirwp.send_control_change(self.CHANNEL, param, color)

    def control_off(self, param):
        """turn off the LEDs under a pad in the top row"""
        midirwp.send_control_change(self.CHANNEL, param, self.CLEAR)

    def _flash_on(self):
        """flashes leds that are configured to flash"""
        self.control_on(0, 0x28)

    def _flash_off(self):
        """turns off flashing"""
        self.control_on(0, 0x25)

    def _flashify(self, color, flash):
        """Returns a flashing or non-flashing version of the color by
        making sure the COPY and CLEAR bits are set to the right
        values."""
        if flash:
            # clear the other buffer and make sure copy is off
            return (color | self.CLEAR) & ~self.COPY
        else:
            # COPY bit overrides CLEAR bit
            return color | Launchpad.COPY


    #
    # MIDI READING
    #


    def read_midi_event(self):
        """Do a blocking read from the device in another thread so we
        don't block the rest of the world."""
        # read only if we are not shutting down
        if self.stop:
            return

        # this should be changed from a true blocking read to an efficient
        # poll with a timeout of, say, a second
        from twisted.internet.threads import deferToThread
        d = deferToThread(midirwp.get_event)
        d.addCallback(self._dispatch_midi_event)

    def _dispatch_midi_event(self, data):
        """dispatch the event to the callback that was registered in
        the constructor and start the next read"""
        print("%-7s 0x%x %s" % (
                'note' if data[0] == self.TYPE_NOTEON else 'control',
                data[2],
                'on' if data[3] > 0 else 'off'))
        self.midi_callback(data)
        self.read_midi_event()

    #
    # PLUGIN HANDLING
    #

    def add_plugin(self, plugin):
        """register the plugin to the pads it wants and set the
        back-reference to the launchpad in the plugin instance"""

        plugin.launchpad = self

        for pad in plugin.pads():
            if pad in self.plugin_map:
                # pad no longer available, error!
                print("Error adding plugin %s: position %x overlaps with plugin %s" %
                      (plugin.__class__, pad, self.plugin_map[pad].__class__))
            else:
                # pad available, add
                self.plugin_map[pad] = plugin

        plugin.setup()

    def get_plugin(self, pad):
        """get the plugin that registered itself to the given pad or None"""
        return self.plugin_map.get(pad)

    #
    # UTILITY FUNCTIONS
    #

    def reset(self):
        """turns off all LEDs, clears all buffers and makes sure flash mode is on"""
        self.control_on(0, 0)
        self._flash_on()

    def shutdown():
        """disconnect from ALSA and the device"""
        stop = True
        midirwp.close()
