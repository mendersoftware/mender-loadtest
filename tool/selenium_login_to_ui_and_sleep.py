#!/usr/bin/env python3

import time
import logging
import os

from selenium import webdriver


sleep_time = 600
url = os.getenv("URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

logs_format = "[%(asctime)s] [%(levelname)-8s] %(message)s"
logging.basicConfig(format=logs_format, level=logging.INFO)
log = logging.getLogger()

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")
options.headless = True
command_executor = "http://localhost:4444/wd/hub"

driver = webdriver.Remote(
    command_executor, desired_capabilities=options.to_capabilities()
)


def site_login():
    log.info("UI: Loggin in as %s to %s" % (username, url))
    driver.get(url)
    driver.find_element_by_id("email").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_id("login_button").click()


site_login()

log.info("UI: going to sleep for %s secs" % sleep_time)
time.sleep(sleep_time)

try:
    log.info("UI: closing driver")
    driver.close()
except Exception:
    pass

log.info("UI: Execution finished.")
