import acitoolkit.acitoolkit as aci


class CiscoACIControllerHTTPClient(object):
    def __init__(self, logger, address, user=None, password=None, scheme="https", port=443):
        """

        :param logging.Logger logger:
        :param str address: controller IP address
        :param str user: controller username
        :param str password: controller password
        :param str scheme: protocol (http|https)
        :param int port: controller port
        """
        full_url = "{}://{}:{}".format(scheme.lower(), address, port)
        self._logger = logger
        self._session = aci.Session(url=full_url, uid=user, pwd=password)
        self._login()

    def _login(self):
        """

        :return:
        """
        resp = self._session.login()

        if not resp.ok:
            self._logger.error("Unable to login to the ACI Controller. HTTP Status code: {} Response: {}"
                               .format(resp.status_code, resp.content))
            raise Exception("Unable to login to the ACI Controller")

    def get_leaf_ports(self):
        """Get leaf ports in the next format: pod->node->slot->port

        :return:
        """
        ports_data = {}
        interfaces = aci.Interface.get(self._session)

        for interface in interfaces:
            if interface.attributes['porttype'].lower() == "leaf":
                nodes = ports_data.setdefault(interface.pod, {})
                slots = nodes.setdefault(interface.node, {})
                ports = slots.setdefault(interface.module, [])
                ports.append({
                    "id": interface.port,
                    "name": interface.name
                })

        return ports_data