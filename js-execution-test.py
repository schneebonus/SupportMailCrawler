from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# target
url = "https://www.bkk-stadt-augsburg.de/seiteninhaltselemente/footermetalinks/impressum.html"
cypher = "jxfiql7fkclXyhh:pqxaq:xrdpyrod+ab"

# selenium config for headless mode and no images
option = webdriver.ChromeOptions()
option.headless = True
chrome_prefs = {}
option.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=option)
# load target page
driver.get(url)
# guess offset
# ToDo: might be able to parse it
offset = range(-10, 10); email = ""
for o in offset:
    # execute js in site context
    js = "return decryptString(\""+cypher+"\","+str(o)+")"
    result = driver.execute_script(js)
    if result.startswith("mailto:") and "@" in result:
        email = result
        break
# print the result and cleanup
print(result); driver.quit()
