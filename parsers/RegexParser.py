# Searchs for e-mails by using regex

import re
from bs4 import BeautifulSoup, SoupStrainer
from .AbstractBaseClassParser import AbstractBaseClassParser

class RegexParser(AbstractBaseClassParser):
    def get_mails_by_regex(soup, VERBOSE):
        email_addresses = set()
        for email in re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[a-zA-Z0-9])", str(soup)):
            if "regex:"+email not in email_addresses and not email.endswith(".png"):
                email_addresses.add("regex:"+email.lower().strip())
                if VERBOSE:
                    print("\t\tregex:" + email)
        return email_addresses

    def extract_mail_addresses(soup, VERBOSE):
        return RegexParser.get_mails_by_regex(soup, VERBOSE)
