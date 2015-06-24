from os.path import dirname

from owncloud.configmanager import ConfigManager

test_dir = dirname(__file__)
temp_config_file = test_dir + '/data/config.php'


def read_file(test_file):
        return open(test_dir + '/data/' + test_file).read()


def test_trusted_config():

    config = ConfigManager(temp_config_file)
    config.write(read_file('config_trusted_domains_input.php'))
    config.trusted('test.domain', 1000)

    assert read_file('config_trusted_domains_output.php') == config.read()


def test_trusted_http_no_port_config():

    config = ConfigManager(temp_config_file)
    config.write(read_file('config_trusted_domains_no_port_input.php'))
    config.trusted('test.domain', 80)

    assert read_file('config_trusted_domains_no_port_output.php') == config.read()


def test_trusted_https_no_port_config():

    config = ConfigManager(temp_config_file)
    config.write(read_file('config_trusted_domains_no_port_input.php'))
    config.trusted('test.domain', 443)

    assert read_file('config_trusted_domains_no_port_output.php') == config.read()


def test_trusted_config_multi_run_ho_harm():

    config = ConfigManager(temp_config_file)
    config.write(read_file('config_trusted_domains_output.php'))
    config.trusted('test.domain', 1000)

    assert read_file('config_trusted_domains_output.php') == config.read()


def test_overwrite_wewroot_config():

    config = ConfigManager(temp_config_file)
    config.write(read_file('config_overwritewebroot_input.php'))
    config.overwrite_webroot()

    assert read_file('config_overwritewebroot_output.php') == config.read()


def test_overwrite_wewroot_existing_config():

    config = ConfigManager(temp_config_file)
    config.write(read_file('config_overwritewebroot_existing_input.php'))
    config.overwrite_webroot()

    read_file('config_overwritewebroot_existing_output.php') == config.read()


def test_overwrite_wewroot_config_multi_run_no_harm():

    config = ConfigManager(temp_config_file)
    config.write(read_file('config_overwritewebroot_existing_output.php'))
    config.overwrite_webroot()

    assert read_file('config_overwritewebroot_existing_output.php') == config.read()
