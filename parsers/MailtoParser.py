# Parses for a href="mailto:..."

from bs4 import BeautifulSoup, SoupStrainer
from .AbstractBaseClassParser import AbstractBaseClassParser


class MailtoParser(AbstractBaseClassParser):
    def get_mails_by_mailto(soup, VERBOSE):
        email_addresses = set()
        for link in soup.find_all('a', href=True):
            if "mailto:" in link['href']:
                if VERBOSE:
                    print("\t\t" + link['href'])
                if (link['href'] not in email_addresses and
                        not link['href'].startswith("mailto:?")):
                    split = link['href'].split("?")[0]
                    email_addresses.add(
                        split.lower().strip().replace(";", "")[7:])
        return email_addresses

    def extract_mail_addresses(soup, VERBOSE):
        return MailtoParser.get_mails_by_mailto(soup, VERBOSE)
