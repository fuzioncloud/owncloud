class Access:
    def __init__(self, config, insider, config_manager, https):
        self.config = config
        self.insider = insider
        self.config_manager = config_manager
        self.https = https

    def set_port(self, protocol, service_type, port):
        self.insider.remove_service(self.config.service_name)
        self.insider.add_service(self.config.service_name, protocol, service_type, port, self.config.url)

    def https_off(self):
        self.https.off()
        self.set_port('http', self.config.service_type_http, self.config.port_http)
        info = self.insider.service_info(self.config.service_name)
        self.config_manager.trusted(info.external_host, info.external_port)

    def https_on(self):
        self.https.on()
        self.set_port('https', self.config.service_type_https, self.config.port_https)
        info = self.insider.service_info(self.config.service_name)
        self.config_manager.trusted(info.external_host, info.external_port)
