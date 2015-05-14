from os.path import dirname, join
import shutil
from syncloud.owncloud.installer import fix_php_raw_post_data, fix_php_charset

test_dir = join(dirname(__file__), 'data')
runtime_dir = join(test_dir, 'runtime')


def test_fix_php_raw_post_data():

    original = join(test_dir, 'php_raw_post_data_original.ini')
    expected = join(test_dir, 'php_raw_post_data_fixed.ini')
    actual = join(runtime_dir, 'php.ini')

    shutil.copyfile(original, actual)
    fix_php_raw_post_data(actual)

    assert open(actual, 'r').read() == open(expected, 'r').read()


def test_fix_php_charset():

    original = join(test_dir, 'php_charset_original.ini')
    expected = join(test_dir, 'php_charset_fixed.ini')
    actual = join(runtime_dir, 'php.ini')

    shutil.copyfile(original, actual)
    fix_php_charset(actual)

    assert open(actual, 'r').read() == open(expected, 'r').read()