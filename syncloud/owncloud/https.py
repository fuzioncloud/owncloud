import os
from subprocess import check_output


apache_owncloud_ssl = "/etc/apache2/sites-available/owncloud-ssl"


def gen_cert(cert_file, key_file):
    openssl_cmd = "openssl req -new -x509 -nodes"
    subj = "/C=US/ST=Denial/L=Springfield/O=Dis/CN=example.com"
    check_output("{} -subj \"{}\" -out {} -keyout {}".format(openssl_cmd, subj, cert_file, key_file), shell=True)


class Https:
    def __init__(self, config):
        self.config = config

    def on(self):
        cert_file = "/etc/ssl/certs/syncloud.crt"
        key_file = "/etc/ssl/private/syncloud.key"
        gen_cert(cert_file, key_file)

        apache_conf = "{}.conf".format(apache_owncloud_ssl)
        with open(apache_conf, 'w') as f:
            f.write("""
            <VirtualHost *:{}>
                ServerName 127.0.0.1
                SSLEngine on
                SSLCertificateFile {}
                SSLCertificateKeyFile {}
                DocumentRoot /var/www
                CustomLog /var/log/apache2/owncloud-ssl-access_log combined
                ErrorLog /var/log/apache2/owncloud-ssl-error_log
            </VirtualHost>
            """.format(self.config.port_https, cert_file, key_file))

        # Fix for apache 2.2
        os.symlink(apache_conf, apache_owncloud_ssl)

        check_output("a2ensite owncloud-ssl", shell=True)
        check_output("a2enmod rewrite", shell=True)
        check_output("a2enmod headers", shell=True)
        check_output("a2enmod ssl", shell=True)
        check_output("service apache2 restart", shell=True)

    def off(self):
        if os.path.isfile(apache_owncloud_ssl):
            check_output("a2dissite owncloud-ssl", shell=True)
        check_output("service apache2 restart", shell=True)