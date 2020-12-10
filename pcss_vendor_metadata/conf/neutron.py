# Copyright 2016 Intel Corporation
# Copyright 2014 OpenStack Foundation
# All Rights Reserved
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
from oslo_config import cfg

from pcss_vendor_metadata.conf import auth
from pcss_vendor_metadata.i18n import _

opts = [
    cfg.IntOpt('retries',
               default=3,
               help=_('Client retries in the case of a failed request.')),
    cfg.IntOpt('request_timeout',
               default=45,
               help=_('Timeout for request processing when interacting '
                      'with Neutron. This value should be increased if '
                      'neutron port action timeouts are observed as neutron '
                      'performs pre-commit validation prior returning to '
                      'the API client which can take longer than normal '
                      'client/server interactions.'))
]
"""extra options except keystone auth options"""


def register_opts(conf):
    conf.register_opts(opts, group='neutron')
    auth.register_auth_opts(conf, 'neutron', service_type='network')


def list_opts():
    _opts = auth.add_auth_opts(opts, service_type='network')
    return [('neutron', _opts), ]
