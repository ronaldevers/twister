from twisted.internet import reactor

from plugin import Plugin
from utils import call

import requests


class Jenkins(Plugin):
    """Shows job status for first 7 jobs in jenkins. This plugin makes
    an http(s) request with http basic auth to the json api in recent
    versions of Jenkins.

    If a job is being built, the pad will flash. Success is green,
    failure is red, disabled is off, other things are orange."""

    height = 1

    def __init__(self, position, options):
        super(Jenkins, self).__init__(position, options)

        if self._get_auth() and not self.get_option('url').startswith('https://'):
            raise Exception("Jenkins plugin: Refusing to do basic auth without https! "
                            "Please change your config.")

        self.query_jenkins()
        self.width = min(7, len(self.jobs))

    def setup(self):
        self.query_jenkins()

        colormap = {'blue': self.launchpad.GREEN,  # success
                    'yellow': self.launchpad.ORANGE,  # unstable
                    'aborted': self.launchpad.ORANGE,  # aborted
                    'grey': self.launchpad.ORANGE,  # pending
                    'red': self.launchpad.RED,  # failed
                    'disabled': self.launchpad.CLEAR}  # disabled

        for index, job in enumerate(self.jobs):
            print job
            color = colormap[job['color'].split('_')[0]]

            self.launchpad.note_on(index + self.position, color,
                                   flash='anime' in job['color'])

        reactor.callLater(60, self.setup)

    def _get_auth(self):
        auth = self.get_option('username'), self.get_option('password')

        # option 1: no auth, ok
        if auth == (None, None):
            return None

        # option 2: bad parameters
        if auth[0] is None or auth[1] is None:
            raise Exception("Jenkins plugin: Error, one of auth username and password "
                            "is given but not both. Please supply both or neither.")

        # option 3: both supplied, ok
        return auth

    def query_jenkins(self):
        response = requests.get(self.get_option('url'), auth=self._get_auth(), verify=False)
        self.jobs = response.json['jobs']

    def pad_down_callback(self, pad):
        call('exo-open', self.jobs[pad]['url'])
