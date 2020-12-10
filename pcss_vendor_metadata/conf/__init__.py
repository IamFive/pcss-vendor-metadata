# -*- coding: utf-8 -*
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
import os

from oslo_config import cfg
from six import moves

from pcss_vendor_metadata.conf import neutron


OPT_GROUP = 'DEFAULT'

API_SERVER_OPTIONS = [
    cfg.StrOpt('listen',
               default="0.0.0.0",
               help='IP address to listen on'),
    cfg.PortOpt('port',
                default=9090,
                help='Port to listen on'),
]


def _fixpath(p):
    """Apply tilde expansion and absolutization to a path."""
    return os.path.abspath(os.path.expanduser(p))


def _search_dirs(dirs, basename, extension=""):
    """Search a list of directories for a given filename.

    Iterator over the supplied directories, returning the first file
    found with the supplied name and extension.

    :param dirs: a list of directories
    :param basename: the filename, for example 'glance-api'
    :param extension: the file extension, for example '.conf'
    :returns: the path to a matching file, or None
    """
    for d in dirs:
        path = os.path.join(d, '%s%s' % (basename, extension))
        if os.path.exists(path):
            return path


def find_config_files():
    """Return a list of default configuration files.

    This is loosely based on the oslo.config version but makes it more
    specific to pcss-vendor-metadata.

    We look for those config files in the following directories:

      ~/.pcss-vendor-metadata/pcss-vendor-metadata.ini
      ~/pcss-vendor-metadata.ini
      /etc/novapcss-vendor-metadata/pcss-vendor-metadata.ini
      /etc/pcss-vendor-metadata.ini
      /etc/pcss-vendor-metadata/pcss-vendor-metadata.ini
    """
    cfg_dirs = [
        _fixpath('~/.pcss-vendor-metadata/'),
        _fixpath('~'),
        '/etc/pcss-vendor-metadata/',
        '/etc'
    ]

    config_files = []
    extension = '.ini'
    config_files.append(
        _search_dirs(cfg_dirs, 'pcss-vendor-metadata', extension))

    return list(moves.filter(bool, config_files))


def register_opts(conf):
    """register metadata server options

    :param conf: oslo conf
    """
    conf.register_opts(API_SERVER_OPTIONS)


def list_opts():
    return [(OPT_GROUP, API_SERVER_OPTIONS), ]


CONF = cfg.CONF

register_opts(CONF)
neutron.register_opts(CONF)
