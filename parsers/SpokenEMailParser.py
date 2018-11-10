import re
from bs4 import BeautifulSoup, SoupStrainer
from .AbstractBaseClassParser import AbstractBaseClassParser

class SpokenEMailParser(AbstractBaseClassParser):

    open_chars = [" ", "[", " [","(", " (", "{", " {"]
    at_chars = ["at", "@"]
    close_chars = [" ", "]", "] ", ")", ") ", "}", "} "]
    dot_chars = ["dot", "punkt", "."]

    def generate_at_list():
        at_list = []
        for o, c in zip(SpokenEMailParser.open_chars, SpokenEMailParser.close_chars):
            for a in SpokenEMailParser.at_chars:
                at_list.append(o+a+c)
        return at_list

    def generate_dot_list():
        dot_list = []
        for o, c in zip(SpokenEMailParser.open_chars, SpokenEMailParser.close_chars):
            for d in SpokenEMailParser.dot_chars:
                dot_list.append(o+d+c)
        return dot_list

    def filter_obfuscation(text):
        at_list = SpokenEMailParser.generate_at_list()
        dot_list = SpokenEMailParser.generate_dot_list()

        nonBreakSpace = u'\xa0'
        text = text.replace(nonBreakSpace, '')
        for at in at_list:
            text = text.replace(at, "@")
        pass
        for dot in dot_list:
            text = text.replace(dot, ".")
        return text

    def extract_mail_addresses(soup, VERBOSE):
        email_addresses = set()
        text = str(soup)
        filtered_text = SpokenEMailParser.filter_obfuscation(text)
        for email in re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[a-zA-Z0-9])", filtered_text):
            if "regex:"+email not in email_addresses  and not email.endswith(".png"):
                email_addresses.add("regex:"+email.lower())
                if VERBOSE:
                    print("\t\tTextToEmail: " + email)
        return email_addresses
