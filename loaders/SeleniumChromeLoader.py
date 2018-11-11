from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .AbstractBaseClassLoader import AbstractBaseClassLoader
import requests
from bs4 import BeautifulSoup
import re


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
        html_deobfuscated = SeleniumChromeLoader.deobfuscate(html)
        soup = BeautifulSoup(html_deobfuscated, "lxml")
        return soup

    def cleanup():
        SeleniumChromeLoader.driver.quit()

    def execute_js(js):
        js_execute = "return " + js
        result = SeleniumChromeLoader.driver.execute_script(js_execute)
        return result

    def deobfuscate(text):
        text = SeleniumChromeLoader.UnCryptMailtoReplace(text)
        text = SeleniumChromeLoader.TextObfuscationReplace(text)
        return text


    def dumbDecrypt(cypher):
        offset = range(-10, 10); email = ""
        for o in offset:
            # execute js in site context
            js = "return decryptString(\""+cypher+"\","+str(o)+")"
            result = SeleniumChromeLoader.driver.execute_script(js)
            if result.startswith("mailto:") and "@" in result:
                email = result
                break
        return email

    def UnCryptMailtoReplace(text):
        m = re.search('javascript:linkTo_UnCryptMailto\(\'(.+?)\'\);', text)
        while m:
            cypher = m.group(1)
            plain = SeleniumChromeLoader.dumbDecrypt(cypher)
            text = text.replace(m.group(0), plain)
            m = re.search('javascript:linkTo_UnCryptMailto\(\'(.+?)\'\);', text)
        return text

    def TextObfuscationReplace(text):
        open_chars = [" ", "[", " [","(", " (", "{", " {"]
        at_chars = ["at", "@"]
        close_chars = [" ", "]", "] ", ")", ") ", "}", "} "]
        dot_chars = ["dot", "punkt", "."]

        at_list = []
        for o, c in zip(open_chars, close_chars):
            for a in at_chars:
                at_list.append(o+a+c)

        dot_list = []
        for o, c in zip(open_chars, close_chars):
            for d in dot_chars:
                dot_list.append(o+d+c)

        nonBreakSpace = u'\xa0'
        text = text.replace(nonBreakSpace, '')
        for at in at_list:
            text = text.replace(at, "@")
        for dot in dot_list:
            text = text.replace(dot, ".")
        return text
