### WARNING: DEPRECATED!!!
### Can't handle javascript

from .AbstractBaseClassLoader import AbstractBaseClassLoader
import requests
from bs4 import BeautifulSoup


class RequestsLoader(AbstractBaseClassLoader):

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    def init():
        pass

    def load_and_soup(target):
        text = ""
        try:
            resp = requests.get(target, allow_redirects=True, headers=RequestsLoader.headers)
            text = resp.text
            resp.connection.close()
        except Exception as e:
            print("exception")
            text = ""

        soup = BeautifulSoup(text, "lxml")
        return soup

    def cleanup():
        pass

    def execute_js(js):
        pass
