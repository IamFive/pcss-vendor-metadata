# Copyright 2016 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys

from oslo_concurrency import processutils
from oslo_log import log
from oslo_service import service
from oslo_service import wsgi

from pcss_vendor_metadata import conf, version
from pcss_vendor_metadata import constants
from pcss_vendor_metadata.common import exception
from pcss_vendor_metadata.conf import CONF

LOG = log.getLogger(__name__)


class WSGIService(service.ServiceBase):
    """Provides ability to launch API from a 'paste' configuration."""

    def __init__(self, name, loader=None):
        """Initialize, but do not start the WSGI server.

        :param name: The name of the WSGI server given to the loader.
        :param loader: Loads the WSGI application using the given name.
        :returns: None

        """
        self.name = name
        self.loader = loader or wsgi.Loader(CONF)
        self.app = self.loader.load_app(name)
        self.host = getattr(CONF, 'listen', "0.0.0.0")
        self.port = getattr(CONF, 'port', 0)
        self.workers = (getattr(CONF, 'workers', None) or
                        processutils.get_worker_count())
        if self.workers and self.workers < 1:
            msg = ("Config option workers has an invalid value %(workers)d "
                   ", the value must be greater than 0." %
                   {'workers': self.workers})
            raise exception.ConfigInvalid(error_msg=msg)

        self.server = wsgi.Server(CONF, name, self.app, host=self.host,
                                  port=self.port)

    def start(self):
        """Start serving this service using loaded configuration.

        Also, retrieve updated port number in case '0' was passed in, which
        indicates a random port should be used.

        :returns: None

        """
        self.server.start()
        self.port = self.server.port
        LOG.info("Starting on port %d" % self.port)

    def stop(self):
        """Stop serving this API.

        :returns: None

        """
        self.server.stop()

    def wait(self):
        """Wait for the service to stop serving this API.

        :returns: None

        """
        self.server.wait()

    def reset(self):
        """Reset server greenpool size to default.

        :returns: None

        """
        self.server.reset()


def process_launcher():
    return service.ProcessLauncher(CONF)


def main():
    log.register_options(CONF)

    # Parse our config
    CONF(sys.argv[1:], project=constants.PROJECT_NAME,
         default_config_files=conf.find_config_files(),
         version=version.version_info.release_string())

    if CONF.debug:
        # Make keystone-middleware emit debug logs
        extra_default_log_levels = ['keystonemiddleware=DEBUG']
        log.set_defaults(default_log_levels=(log.get_default_log_levels() +
                                             extra_default_log_levels))

    # Set us up to log as well
    log.setup(CONF, constants.PROJECT_NAME)
    if CONF.debug:
        CONF.log_opt_values(LOG, log.DEBUG)

    server = WSGIService(constants.PROJECT_NAME)
    launcher = process_launcher()
    launcher.launch_service(server, workers=server.workers)
    launcher.wait()


if __name__ == '__main__':
    sys.exit(main())
