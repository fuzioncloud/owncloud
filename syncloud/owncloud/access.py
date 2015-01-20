from os.path import join


class Access:
    def __init__(self, config, insider, config_manager, apache):
        self.apache = apache
        self.config = config
        self.insider = insider
        self.config_manager = config_manager
        self.site_config_file_full = join(config.config_path, config.site_config_file)

    def set_port(self, protocol, service_type, port):
        self.insider.remove_service(self.config.service_name)
        self.insider.add_service(self.config.service_name, protocol, service_type, port, self.config.url)

    def https_off(self):
        self.apache.remove_https_site(self.config.site_name)
        self.apache.add_http_site(self.config.site_name, self.site_config_file_full)
        self.apache.restart()

        self.set_port('http', self.config.service_type_http, self.config.port_http)
        info = self.insider.service_info(self.config.service_name)
        self.config_manager.trusted(info.external_host, info.external_port)

    def https_on(self):
        self.apache.remove_http_site(self.config.site_name)
        self.apache.add_https_site(self.config.site_name, self.site_config_file_full)
        self.apache.restart()

        self.set_port('https', self.config.service_type_https, self.config.port_https)
        info = self.insider.service_info(self.config.service_name)
        self.config_manager.trusted(info.external_host, info.external_port)
