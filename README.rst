Twister for Novation Launchpad
==============================

The Novation Launchpad is a MIDI controller with 9x9 (minus 1) grid of
LED-colored push-buttons. Twister captures key presses and key releases from
the device and lets you bind actions to those events.

Usage
-----

Run ``make`` in the c directory to compile the midirwp Python extension module.

Next, call the ``launch.sh`` script in the python directory. You should provide a
config file with ``-c`` and a midi port with ``-p``. See also ``launch.sh -h``.::

    cd c && make && cd ../python
    ./launch.sh -p 24 -c twister.example.conf

Run ``arecordmidi -l`` to find the port number. Remove the trailing ``:0``, so
``24:0`` becomes simply port ``24``.

Config
------

See ``twister.example.conf`` for an example of how the config file works. It is
just an ini-style file with a [section] for every plugin. If the plugin has a
different name then the section, then put a ``plugin = ..`` line in the section.
Section names must be unique. Only the position attribute is mandatory. It
specifies the absolute position on the launchpad of the first pad of the
plugin. It is easy to give extra values to a plugin from the configfile since
all options in a plugin's section are passed to the plugin's constructor and
can be easily looked up through the ``Plugin::get_option`` method.

Plugins
-------

Twister comes with a bunch of plugins:

- AppRaiser: uses wmctrl to raise application windows by their window
  class

- Exo: for opening lots of stuff with exo-open, for example web urls

- Git: sends keystrokes to your (focussed) terminal window

- Jenkins: show jenkins job statuses, pressing the pad for a failed job will
  open the jenkins web interface for that job

- Mpg123: plays mp3's using mpg123 (use for BADOOMTISH, drumrolls and most
  imporantly rickrolls)

- Simple: for simply calling an external utility, possibly with static
  arguments

- Spotify: for controlling Spotify playback (uses DBUS)

- Volume: for controlling alsa system volume

- WorkspaceSwitcher: uses wmctrl to switch workspaces

- XRandR: quick access to xrandr for auto, mirrored or extended desktops


Writing Plugins
---------------

Writing a custom plugin is really easy! Take a look at the existing plugins for
inspiration. The basic idea is:

- subclass the Plugin class

- make sure that a width and height attribute is set when the constructor
  finishes

- override the pad_down_callback and/or pad_up_callback mehods

- if you want to do setup, do it by overriding the setup method, not in the
  constructor, the difference being that in setup you have the launchpad object
  at your disposal

- if you just want to call some external command when you depress a pad, the
  provided 'Simple' plugin will do just that for you
