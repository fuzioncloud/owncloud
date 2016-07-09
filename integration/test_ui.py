from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import dirname, join, exists, abspath, isdir
import os
import sys
import shutil
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
log_dir = join(LOG_DIR, 'owncloud_log')


def test_web_with_selenium(user_domain):

    os.environ['PATH'] = os.environ['PATH'] + ":" + join(DIR, 'geckodriver')

    caps = DesiredCapabilities.FIREFOX
    caps["marionette"] = True
    caps["binary"] = "/usr/bin/firefox"

    profile = webdriver.FirefoxProfile()
    profile.set_preference("webdriver.log.file", "{0}/firefox.log".format(log_dir))
    driver = webdriver.Firefox(profile, capabilities=caps)
    driver.get("http://{0}".format(user_domain))
    user = driver.find_element_by_id("user")
    user.send_keys(DEVICE_USER)
    password = driver.find_element_by_id("password")
    password.send_keys(DEVICE_PASSWORD)
    password.submit()
    wait_driver = WebDriverWait(driver, 10)
    wait_driver.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#header #expandDisplayName'), DEVICE_USER))

    screenshot_dir = join(DIR, 'screenshot')
    if exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.mkdir(screenshot_dir)
    driver.get_screenshot_as_file(join(screenshot_dir, 'admin.png'))