class Config:

    def __init__(self, service_name, port_http, service_type_http, port_https, service_type_https, url, config_file,
                 site_config_file, site_name, config_path):
        self.service_name = service_name
        self.port_http = port_http
        self.service_type_http = service_type_http
        self.port_https = port_https
        self.service_type_https = service_type_https
        self.url = url
        self.config_file = config_file
        self.site_config_file = site_config_file
        self.site_name = site_name
        self.config_path = config_path
