# Requires Splash!
# Splash is a javascript rendering service with an HTTP API.
# It's a lightweight browser with an HTTP API, implemented in Python 3 using Twisted and QT5.
# It's fast, lightweight and state-less which makes it easy to distribute.
#
# Link: https://splash.readthedocs.io/en/stable/install.html#linux-docker
# 1. install, enable and start docker
# 2. sudo docker pull scrapinghub/splash
# 3. sudo docker run -p 8050:8050 -p 5023:5023 scrapinghub/splash

import requests
from bs4 import BeautifulSoup

from .AbstractBaseClassLoader import AbstractBaseClassLoader

class SplashLoader(AbstractBaseClassLoader):
    def render_and_js(target):
        slash_server = "localhost"
        slash_port = 8050
        url = "http://" + slash_server + ":" + str(slash_port) + "/render.html?url=" + target + "&timeout=10&wait=0&images=0"
        re = requests.get(url)
        text = re.text
        return text

    def load_and_soup(target):
        text = SplashLoader.render_and_js(target)
        soup = BeautifulSoup(text, "lxml")
        return soup
