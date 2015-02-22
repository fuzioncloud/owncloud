from os.path import join


class Access:
    def __init__(self, config, insider, config_manager, apache):
        self.apache = apache
        self.config = config
        self.insider = insider
        self.config_manager = config_manager
        self.site_config_file_full = join(config.config_path, config.site_config_file)

    def update_insider(self, protocol, service_type, port):
        self.insider.remove_service(self.config.service_name)
        self.insider.add_service(self.config.service_name, protocol, service_type, port, self.config.url)

        info = self.insider.service_info(self.config.service_name)
        self.config_manager.trusted(info.external_host, info.external_port)

    def enable_http_web(self):
        self.apache.remove_https_site(self.config.site_name)
        self.apache.add_http_site(self.config.site_name, self.site_config_file_full)
        self.apache.restart()

    def mode(self, protocol):
        if protocol == 'https':
            self.enable_https_web()
            self.update_insider('https', self.config.service_type_https, self.config.port_https)
        elif protocol == 'http':
            self.enable_http_web()
            self.update_insider('http', self.config.service_type_http, self.config.port_http)
        self.config_manager.overwrite_webroot()

    def enable_https_web(self):
        self.apache.remove_http_site(self.config.site_name)
        self.apache.add_https_site(self.config.site_name, self.site_config_file_full)
        self.apache.restart()