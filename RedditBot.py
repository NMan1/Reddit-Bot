from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from .AccountCracker import wait_for_element
from flask import render_template
import time
import zipfile
import os
from selenium.webdriver.chrome.options import Options

## post - comment
karma = []


def get_chromedriver(use_proxy=False, user_agent=None):
    ip = '194.110.192.137'
    port = 3128
    username = 'foo'
    password = 'bar'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%(ip)s",
                port: %(port)s
            }
            }
        }
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%(username)s",
                password: "%(password)s"
            }
        }
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    )
    """ % {'ip': ip, 'port': port, 'username': username, 'password': password}

    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_extension(plugin_file)
    driver = webdriver.Chrome(
        "/chromedriver.exe",
        options=chrome_options)
    return driver


class Website:
    def __init__(self, do_driver, driver, username, password, url):
        self.url = url
        self.username = username
        self.password = password

        if do_driver:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-notifications")
            # options.add_argument("headless")
            self.driver = webdriver.Chrome("/chromedriver.exe", options=options)
            self.driver.get("https://www.reddit.com/login/")
        else:
            self.driver = driver
            self.driver.get("https://www.reddit.com/login/")

    def login(self):
        user = self.driver.find_element_by_id("loginUsername")
        passw = self.driver.find_element_by_id("loginPassword")
        user.click()
        user.send_keys(self.username)
        passw.click()
        passw.send_keys(self.password)
        self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/form/fieldset[5]/button").click()

    def send_comment(self, comment):
        wait_for_element(self.driver, "/html/body/div[1]/div/div/div/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div/div")

        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div/div").send_keys(comment)
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/div[1]/button").click()


def run(username, password, vars):
    if vars[1] == True:
        driver = get_chromedriver(True)
        web = Website(False, driver, username, password, vars[2])
    else:
        web = Website(True, None, username, password, vars[2])

    web.driver.set_page_load_timeout(15)
    web.login()
    time.sleep(1)
    web.driver.get(web.url)
    web.driver.get(web.url)

    comment = vars[3] + "\n\n" + vars[4] 
    index = 0
    while index < int(vars[5]):
        web.send_comment(comment)
        time.sleep(3)
        index += 1

    web.driver.quit()
