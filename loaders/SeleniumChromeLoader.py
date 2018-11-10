from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .AbstractBaseClassLoader import AbstractBaseClassLoader
import requests
from bs4 import BeautifulSoup


class SeleniumChromeLoader(AbstractBaseClassLoader):
    driver = None

    def init():
        option = webdriver.ChromeOptions()
        option.headless = True
        chrome_prefs = {}
        option.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

        CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
        SeleniumChromeLoader.driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=option)

    def load_and_soup(target):
        SeleniumChromeLoader.driver.get(target)
        html = SeleniumChromeLoader.driver.page_source
        soup = BeautifulSoup(html, "lxml")
        return soup

    def cleanup():
        SeleniumChromeLoader.driver.quit()
