from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .AbstractBaseClassLoader import AbstractBaseClassLoader
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse as urlparse


class SeleniumChromeLoader(AbstractBaseClassLoader):
    driver = None
    x = 1920
    y = 1080

    def init():
        option = webdriver.ChromeOptions()
        option.add_argument("--disable-background-networking")
        option.add_argument("--safebrowsing-disable-auto-update")
        option.add_argument("--disable-syn")
        option.add_argument("--metrics-recording-only")
        option.add_argument("--disable-default-apps")
        option.add_argument("--mute-audio")
        option.add_argument("--no-first-run")
        option.add_argument("--disable-background-timer-throttling")
        option.add_argument("--disable-client-side-phishing-detection")
        option.add_argument("--disable-popup-blocking")
        option.add_argument("--disable-prompt-on-repost")
        option.add_argument("--enable-automation")
        option.add_argument("--password-store=basic")
        option.add_argument("--use-mock-keychain")
        option.add_argument("--disable-component-update")
        option.add_argument("--disable-notifications")
        option.add_argument("--disable-hang-monitor")
        option.add_argument("--disable-gpu")
        # option.add_argument("--headless")
        option.headless = True
        chrome_prefs = {}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {
            "images": 2}
        chrome_prefs["custom_handlers.enabled"] = True
        option.experimental_options["prefs"] = chrome_prefs
        CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
        SeleniumChromeLoader.driver = webdriver.Chrome(
            CHROMEDRIVER_PATH, chrome_options=option)
        SeleniumChromeLoader.driver.set_window_size(
            SeleniumChromeLoader.x, SeleniumChromeLoader.y)

    def current_url():
        return SeleniumChromeLoader.driver.current_url

    def navigate_to_url(url):
        SeleniumChromeLoader.driver.get(url)
        target = SeleniumChromeLoader.driver.current_url
        return target

    def click_link_by_name(name):
        link = SeleniumChromeLoader.driver.find_element_by_link_text(name)
        link.click()
        target = SeleniumChromeLoader.driver.current_url
        return target

    def get_plain_content(target):
        html = SeleniumChromeLoader.driver.page_source
        html_deobfuscated = SeleniumChromeLoader.deobfuscate(html, target)
        return html_deobfuscated

    def load_and_soup(target):
        html = SeleniumChromeLoader.driver.page_source
        html_deobfuscated = SeleniumChromeLoader.deobfuscate(html, target)
        soup = BeautifulSoup(html_deobfuscated, "lxml")
        return soup

    def cleanup():
        SeleniumChromeLoader.driver.quit()

    def execute_js(js):
        js_execute = js
        result = SeleniumChromeLoader.driver.execute_script(js_execute)

        return result

    def deobfuscate(text, target):
        text = SeleniumChromeLoader.decrypt_by_injecting_returns(text)
        # text = SeleniumChromeLoader.UnCryptMailtoReplace(text)
        text = SeleniumChromeLoader.TextObfuscationReplace(text)
        text = SeleniumChromeLoader.remove_hidden_spans(text)
        return text

    def clickDecrypt(text, target):
        m = re.search('javascript:linkTo_UnCryptMailto\(\'(.+?)\'\);', text)
        while m:
            js = m.group(0).replace("javascript:", "")
            result = SeleniumChromeLoader.execute_js(js)
            redirected = SeleniumChromeLoader.driver.current_url
            parsed = urlparse.urlparse(redirected)
            print(redirected)
            email = urlparse.parse_qs(parsed.query)['grabme'][0]
            text = text.replace(m.group(0), email)
            m = re.search(
                'javascript:linkTo_UnCryptMailto\(\'(.+?)\'\);', text)
            SeleniumChromeLoader.driver.get(target)
        return text

    # https://www.universa.de/ueber-uns/impressum/impressum.htm
    def remove_hidden_spans(text):
        soup = BeautifulSoup(text, "lxml")
        for hidden_span in soup.find_all('span', {'style': 'display:none'}):
            hidden_span.clear()
        return soup.prettify()

    def replace_return(original_function):
        return_function = original_function.replace(
            "window.location.href=", "return ")
        return_function = return_function.replace(
            "window.location.href =", "return")
        return_function = return_function.replace(
            "top.location.href =", "return")
        return_function = return_function.replace(
            "top.location.href=", "return ")
        return_function = return_function.replace(
            "location.href =", "return")
        return_function = return_function.replace(
            "location.href=", "return ")
        return return_function

    def decrypt_by_injecting_returns(text):
        encryption_functions = [
            "linkTo_UnCryptMailto", "decryptMail", "mailthis"]
        for encryption_function in encryption_functions:
            try:
                m = re.search(encryption_function + r'\(\'(.+?)\'\)', text)
                while m:
                    js = m.group(0).replace("javascript:", "")
                    original_function = SeleniumChromeLoader.execute_js(
                        "var t = " + encryption_function + ".toString(); return t")
                    return_function = SeleniumChromeLoader.replace_return(
                        original_function)
                    email = SeleniumChromeLoader.execute_js(
                        return_function + "; return " + js)
                    # clean original html and replace js-call with its result
                    text = text.replace("javascript:" + m.group(0), email)
                    text = text.replace(m.group(0), email)
                    m = re.search(
                        r'javascript:' + encryption_function +
                        r'\(\'(.+?)\'\);', text)
            except Exception as e:
                print("Error: Site is using " + encryption_function + " but does not provide function.")
        return text

    def replace_return(original_function):
        return_function = original_function.replace(
            "window.location.href=", "return ")
        return_function = return_function.replace(
            "window.location.href =", "return")
        return_function = return_function.replace(
            "top.location.href =", "return")
        return_function = return_function.replace(
            "top.location.href=", "return ")
        return_function = return_function.replace(
            "location.href =", "return")
        return_function = return_function.replace(
            "location.href=", "return ")
        return return_function

    def dumbDecrypt(cypher):
        offset = range(-10, 10)
        email = ""
        for o in offset:
            # execute js in site context
            js = "return decryptString(\"" + cypher + "\"," + str(o) + ")"
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
            m = re.search(
                'javascript:linkTo_UnCryptMailto\(\'(.+?)\'\);', text)
        return text

    def TextObfuscationReplace(text):
        open_chars = [" ", "[", " [", "(", " (", "{", " {"]
        at_chars = ["at", "@"]
        close_chars = [" ", "]", "] ", ")", ") ", "}", "} "]
        dot_chars = ["dot", "punkt", "."]

        at_list = []
        for o, c in zip(open_chars, close_chars):
            for a in at_chars:
                at_list.append(o + a + c)

        dot_list = []
        for o, c in zip(open_chars, close_chars):
            for d in dot_chars:
                dot_list.append(o + d + c)

        nonBreakSpace = u'\xa0'
        text = text.replace(nonBreakSpace, '')
        for at in at_list:
            text = text.replace(at, "@")
        for dot in dot_list:
            text = text.replace(dot, ".")
        return text
