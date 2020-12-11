pcss-vendor-metadata
====================


Overview
========

This project aims to offer NOVA vendor metadata service for PCSS HPC cloud.
Only `Mellanox SR-IOV binding details` data is served currently, it's served
as 


How it works
============

This project is designed according to official `NOVA vendordata`_ document.

The vendordata feature provides a way to pass vendor or deployment-specific
information to instances. This can be accessed by users using the metadata
service or with config-drives. There are two vendordata modules provided by
nova: StaticJSON and DynamicJSON. In this project, `DynamicJSON` is used.
The DynamicJSON vendordata transmits as fellow:

::

      curl http://169.254.169.254/openstack/latest/vendor_data2.json
    --------------+--------------------------------------------------->
                  |
    +----------+  |   +----------------------+     +-------------------+
    + Instance +--+-->+ Neutron Metadata API +---->+ NOVA Metadata API +
    +----------+      +----------------------+     +----------+--------+
                                                              |
                                                  load DynamicJSON vendordata
                                                              |
                                                              V
    +----------------------+      Query Mlnx       +----------+----------+
    + Neutron Service API  +<----   SR-IOV  -------+ Vendor Metadata API +
    +----------------------+    binding details    +---------------------+


The DynamicJSON vendordata is a bit different from other metadata, cloud-init
OpenStack-datasource does not load DynamicJSON vendordata automatically. So,
end-user needs to fetch and process DynamicJSON vendordata manually, typically,
this action can be triggered by a customized cloud-init module like `runcmd`
or a crafted image with customized init service run after cloud-init final
service. For PCSS HPC cloud, `mellanox-sriov` element of `DIB FOR PCSS`_ is
offered to consume the vendor data and config Mellanox SR-IOV ports.
The `mellanox-sriov` element uses a customized init service to load
DynamicJSON vendordata and creates Mellanox SR-IOV ports dynamically.


Note::

Reading both user and admin guid of `NOVA vendor data`_ before using this
service, and `Michael Still's talk`_ from the Queens summit in Sydney will
give you more details about how the whole workflow works.


Installation
=============

This service should be installed on nodes which:

- can be accessed from OpenStack NOVA node
- can access OpenStack Keystone service
- can access OpenStack Neutron service

You may install it through from source:

.. code-block:: bash

   $ git clone https://github.com/IamFive/pcss-vendor-metadata.git
   $ cd pcss-vendor-metadata
   $ git checkout stable/train
   $ sudo pip install -r requirements.txt -c upper-constraints.txt
   $ sudo python setup.py install


Quick Start
===========

After installed, several config/sample files will be copied to
`/etc/pcss-vendor-metadata`:

- pcss-vendor-metadata-api-paste.ini
- pcss-vendor-metadata.ini.sample
- pcss-vendor-metadata-server.service.sample

To have a quick start, duplicate and rename `pcss-vendor-metadata.ini.sample`
file to `pcss-vendor-metadata.ini`, and update the options(mainly
keystone/neutron authentication options) :

.. code-block:: bash

   $ cd /etc/pcss-vendor-metadata
   $ cp pcss-vendor-metadata.ini.sample pcss-vendor-metadata.ini
   # update options
   $ sudo vi pcss-vendor-metadata.ini

Then, run vendordata metadata service through:

.. code-block:: bash

   $ sudo pcss-vendor-metadata-svc

If `systemd` init system is used, to run metadata service with systemd:

.. code-block:: bash

   $ cd /etc/pcss-vendor-metadata
   $ sudo cp pcss-vendor-metadata-server.service.sample \
        /usr/lib/systemd/system/pcss-vendor-metadata-server.service
   $ groupadd nova
   $ useradd -g nova nova
   $ sudo systemctl enable pcss-vendor-metadata-server.service
   $ sudo systemctl start pcss-vendor-metadata-server.service


Configuration
=============

HTTP socket binding Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project serves DynamicJSON vendordata through HTTP protocol using WSGI,
so, configuration options for socket binding is required, you may generate it
through oslo-config-generator:

.. code-block:: bash

    $ oslo-config-generator --namespace  pcss.vendordata.service


The default configurations may looks like:

.. code-block:: ini

    [DEFAULT]

    #
    # From pcss.vendordata.service
    #

    # IP address to listen on (string value)
    #listen = 0.0.0.0

    # Port to listen on (port value)
    # Minimum value: 0
    # Maximum value: 65535
    #port = 9090


Neutron Client Options
^^^^^^^^^^^^^^^^^^^^^^

This project need to communicate with Neutron to query Mellanox SR-IOV
binding details (like virtual GUID info), python-neutronclient is used to
archive this goal. Authentication and connection options is required for
this communication, you may generate it through:

.. code-block:: bash

    $ oslo-config-generator --namespace  pcss.vendordata.neutron

Other Options
^^^^^^^^^^^^^

This project also uses several other components that has configuration options:

- keystonemiddleware:
    This package contains middleware modules designed to
    provide authentication and authorization features to web services other
    than Keystone.

    To generate the configuration options:

    .. code-block:: bash

        # for keystonemiddleware (required)
        $ oslo-config-generator --namespace keystonemiddleware.auth_token

- oslo.service:
    oslo.service provides a framework for defining new
    long-running services using the patterns established by other OpenStack
    applications. It also includes utilities long-running applications
    might need for working with SSL or WSGI, performing periodic operations,
    interacting with systemd, etc.

    To generate the configuration options:

        # for oslo.service (required)
        $ oslo-config-generator --namespace oslo.service.periodic_task
        $ oslo-config-generator --namespace oslo.service.service
        $ oslo-config-generator --namespace oslo.service.sslutils
        $ oslo-config-generator --namespace oslo.service.wsgi

    It is not necessary to update most of the options generated upon for
    `oslo.service`, only `api_paste_config` option is required, the value
    should be `/etc/pcss-vendor-metadata/pcss-vendor-metadata-api-paste.ini`

    .. code-block:: ini

        [DEFAULT]

        #
        # From oslo.service.wsgi
        #

        # File name for the paste.deploy config for api service (string value)
        #api_paste_config = api-paste.ini


Integration
===========

Document `NOVA Metadata Service`_ describes how to config and enable Nova
metadata service, and `NOVA vendordata`_ document can help you setup Dynamic
vendordata metadata service.

Be caution that to cooperation with `mellanox-sriov` element mentioned upon,
the dynamic target name should be `mlnx_sriov`. So, the final configuration
may looks like:

.. code-block:: ini

    [api]
    vendordata_providers=DynamicJSON,...
    vendordata_dynamic_targets=mlnx_sriov@http://domain:9090,....

    [vendordata_dynamic_auth]
    ....


.. _NOVA Metadata Service: https://docs.openstack.org/nova/latest/admin/metadata-service.html
.. _PCSS vendor metadata: https://github.com/IamFive/pcss-vendor-metadata
.. _NOVA vendordata: https://docs.openstack.org/nova/train/admin/vendordata.html
.. _Michael Still's talk: https://www.openstack.org/videos/summits/sydney-2017/metadata-user-data-vendor-data-oh-my
.. _DIB FOR PCSS: https://github.com/IamFive/diskimage-builder/tree/pcss/diskimage_builder
