# Searchs for e-mails by using regex

import re
from bs4 import BeautifulSoup, SoupStrainer
from .AbstractBaseClassParser import AbstractBaseClassParser


class RegexParser(AbstractBaseClassParser):
    def extract_mail_addresses(soup, VERBOSE, tld):
        email_addresses = set()
        regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[a-zA-Z0-9])"
        for email in re.findall(regex, str(soup)):
            email = email.lower().strip()
            if (email not in email_addresses
                    and tld.is_valid_tld(email)):
                email_addresses.add(email)
                if VERBOSE:
                    print("\t\tregex:" + email)
        return email_addresses
