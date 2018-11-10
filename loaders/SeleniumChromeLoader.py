from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .AbstractBaseClassLoader import AbstractBaseClassLoader
import requests
from bs4 import BeautifulSoup


class SeleniumChromeLoader(AbstractBaseClassLoader):
    def load_and_soup(target):
        options = Options()
        options.headless = True
        CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
        driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=options)
        driver.get(target)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        return soup
