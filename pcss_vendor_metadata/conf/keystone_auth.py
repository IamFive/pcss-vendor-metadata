from keystoneauth1 import loading as ks_loading

GROUP_NAME = 'keystone_authtoken'


def list_keystoneauth_opts():
    return [(GROUP_NAME, (
            ks_loading.get_auth_common_conf_options() +
            ks_loading.get_auth_plugin_conf_options('password')))]
