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
from neutronclient.v2_0 import client as client_v20

from pcss_vendor_metadata.common import keystone
from pcss_vendor_metadata.conf import CONF


_NEUTRON_SESSION = None


def _get_neutron_session():
    global _NEUTRON_SESSION
    if not _NEUTRON_SESSION:
        _NEUTRON_SESSION = keystone.get_session('neutron',
                                                timeout=CONF.neutron.timeout)
    return _NEUTRON_SESSION


def get_client(token=None):
    session = _get_neutron_session()
    service_auth = keystone.get_auth('neutron')
    endpoint = keystone.get_endpoint('neutron', session=session,
                                     auth=service_auth)

    user_auth = None
    if CONF.neutron.auth_type != 'none' and token:
        user_auth = keystone.get_service_auth(endpoint, token, service_auth)

    return client_v20.Client(session=session,
                             auth=user_auth or service_auth,
                             endpoint_override=endpoint,
                             retries=CONF.neutron.retries,
                             timeout=CONF.neutron.request_timeout)
