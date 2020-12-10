#!/usr/bin/python
import json

from oslo_log import log
from webob import Response
from webob.dec import wsgify

from pcss_vendor_metadata.common import neutron_client
from pcss_vendor_metadata.i18n import _

LOG = log.getLogger(__name__)

BD_ENABLE_SRIOV = 'enable_sriov'
BD_DFT_LIMITED_PKEYS = 'default_limited_pkeys'
BD_PHYSICAL_GUIDS = 'physical_guids'
BD_VIRTUAL_GUIDS = 'virtual_guids'
BD_DYNAMIC_PKEY = 'dynamic_pkey'


def app_factory(global_config, **local_config):
    LOG.info("global_config %(global_config)s, local_config %(local_config)s",
             {'global_config': global_config, 'local_config': local_config})
    return application


@wsgify
def application(req):
    # in case delay_auth_decision is set to True.
    if req.environ.get('HTTP_X_IDENTITY_STATUS') != 'Confirmed':
        return Response('Not authenticated.', status=401)

    # NOTE(qianbiao.ng) policies validation

    try:
        # Get the data nova handed us for this request
        # An example of this data:
        # {
        #     "hostname": "foo",
        #     "image-id": "75a74383-f276-4774-8074-8c4e3ff2ca64",
        #     "instance-id": "2ae914e9-f5ab-44ce-b2a2-dcf8373d899d",
        #     "metadata": {},
        #     "project-id": "039d104b7a5c4631b4ba6524d0b9e981",
        #     "user-data": null
        # }

        data = req.environ.get('wsgi.input').read()
        if not data:
            return Response('No instance metadata provided', status=500)

        instance = json.loads(data)
        LOG.debug(_("Receive getting vendor data request from instance: "
                    "%(instance)s"),
                  {'instance': instance})

        # data = req.environ.get('wsgi.input').read()
        # if not data:
        #     return Response('No instance metadata provided', status=500)
        # instance_info = json.loads(data)
        # LOG.debug(_("Receive new request from instance: %(instance)s"),
        #           {'instance': instance_info})

        instance_id = instance.get('instance-id')
        client = neutron_client.get_client()
        ports_meta = client.list_ports(device_id=instance_id, retrieve_all=True)
        ports = ports_meta.get('ports')
        if len(ports) == 0:
            msg = _("No ethernet port is allocated for "
                    "instance: %(instance)s").format({'instance': instance_id})
            LOG.error(msg)
            return Response(msg, status=500)

        # NOTE(qianbiao.ng): Multiple tenant network is not support indeed.
        """
        binding_details_list = []
        for port in ports:
            vif_details = port.get("binding:vif_details", {})
            sriov_enabled = vif_details.get(BD_ENABLE_SRIOV, False)
            if sriov_enabled:
                binding_details_list.append({
                    BD_ENABLE_SRIOV: vif_details.get(BD_ENABLE_SRIOV),
                    BD_DFT_LIMITED_PKEYS: vif_details.get(BD_DFT_LIMITED_PKEYS),
                    BD_PHYSICAL_GUIDS: vif_details.get(BD_PHYSICAL_GUIDS),
                    BD_VIRTUAL_GUIDS: vif_details.get(BD_VIRTUAL_GUIDS),
                    BD_DYNAMIC_PKEY: vif_details.get(BD_DYNAMIC_PKEY),
                })
        """

        # First port's binding VIF details will be used to create SRIOV ports.
        port = ports[0]
        vif_details = port.get("binding:vif_details", {})

        response_vif_details = {}
        sriov_enabled = vif_details.get(BD_ENABLE_SRIOV, False)
        if sriov_enabled:
            response_vif_details = {
                BD_ENABLE_SRIOV: vif_details.get(BD_ENABLE_SRIOV),
                BD_DFT_LIMITED_PKEYS: vif_details.get(BD_DFT_LIMITED_PKEYS),
                BD_PHYSICAL_GUIDS: vif_details.get(BD_PHYSICAL_GUIDS),
                BD_VIRTUAL_GUIDS: vif_details.get(BD_VIRTUAL_GUIDS),
                BD_DYNAMIC_PKEY: vif_details.get(BD_DYNAMIC_PKEY),
            }

        return Response(
            json.dumps(response_vif_details, indent=4, sort_keys=True))

    except Exception as e:
        LOG.exception(_("Failed to process request: %(req)s"), {'req': req})
        return Response('Internal Server Error', status=500)
