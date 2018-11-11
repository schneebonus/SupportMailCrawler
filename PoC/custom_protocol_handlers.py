from selenium import webdriver
from selenium.webdriver.chrome.options import Options

protocols = [{
                'default' : True,
                'protocol' : 'mailto',
                'title' : 'f5w-mailhandler',
                'url' : 'https://f5w.de?url=%s'
            }]

option = webdriver.ChromeOptions()
#option.headless = True
chrome_prefs = {}
option.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
chrome_prefs["custom_handlers.enabled"] = True
chrome_prefs["custom_handlers.registered_protocol_handlers"] = protocols
option.experimental_options["prefs"] = chrome_prefs
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=option)
driver.get("mailto:abc@abc.de")
driver.quit()
