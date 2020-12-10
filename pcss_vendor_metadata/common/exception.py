# Copyright 2019 HUAWEI, Inc. All Rights Reserved.
# Copyright 2017 Red Hat, Inc. All Rights Reserved.
# Modified upon https://github.com/openstack/sushy
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from pcss_vendor_metadata.i18n import _

LOG = logging.getLogger(__name__)


class VendorMetadataException(Exception):
    """Basic exception"""

    message = None

    def __init__(self, **kwargs):
        if self.message and kwargs:
            self.message = self.message % kwargs

        super(VendorMetadataException, self).__init__(self.message)


class CatalogNotFound(VendorMetadataException):
    message = _("Service type %(service_type)s with endpoint type "
                "%(endpoint_type)s not found in keystone service catalog.")


class KeystoneUnauthorized(VendorMetadataException):
    _msg_fmt = _("Not authorized in Keystone.")


class ConfigInvalid(VendorMetadataException):
    _msg_fmt = _("Invalid configuration file. %(error_msg)s")


class KeystoneFailure(VendorMetadataException):
    pass
