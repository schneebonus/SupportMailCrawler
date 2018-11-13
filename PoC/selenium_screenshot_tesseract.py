from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
y = 4000
target = "https://www.uni-giessen.de/ueber-uns/datenschutz"

# lets rock!
print("Resizing window to: " + str(x) + "x" + str(y))
driver.set_window_size(x, y)
print("Loading website: " + target)
driver.get(target)
print("Taking a screenshot")
driver.save_screenshot('screenshot.png')
print("Screenshot -> Tesseract -> Text")
text = pytesseract.image_to_string(Image.open('screenshot.png'))
print("If @ in token -> print!")
for line in text.split("\n"):
    for token in line.split(" "):
        if "@" in token:
            print("\t" + token)
