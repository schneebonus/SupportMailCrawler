from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


# init chrome
option = webdriver.ChromeOptions()
option.headless = True
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
driver = webdriver.Chrome(
    CHROMEDRIVER_PATH, chrome_options=option)

# set parameters
x = 1920
y = 1080
target = "https://www.uni-giessen.de/ueber-uns/datenschutz"

# lets rock!
print("Resizing window to: " + str(x) + "x" + str(y))
driver.set_window_size(x, y)
print("Loading website: " + target)
driver.get(target)
print("Building a custom wordlist (based on the html content)")
print("Taking a screenshot")
driver.save_screenshot('screenshot.png')
print("Screenshot -> Tesseract -> Text")
config = ('--psm 11 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@-.')
text = pytesseract.image_to_string(Image.open('screenshot.png'), config=config)
print("If @ in token -> print!")
for line in text.split("\n"):
    for token in line.split(" "):
        if "@" in token:
            print("\t" + token)
