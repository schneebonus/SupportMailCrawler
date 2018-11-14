# E-Mail-crawler
# by Mark Schneemann
#
# Usage:
# python3 mail-crawler.py <crawling_depth> -u <target>
# python3 mail-crawler.py <crawling_depth> -l <list.csv>#
#
# Optional: add -v for verbose mode
#
# Examples:
# python3 mail-crawler.py 2 -u https://privacyscore.org
# python3 mail-crawler.py 3 -l lists/InstitutionsOfHigherEducation.csv
# ------------------------------ Config ------------------------------

from enum import Enum
import traceback
import tldextract
import argparse
import requests
import urllib
import urllib.request
from parsers.RegexParser import RegexParser
from parsers.MailtoParser import MailtoParser
from loaders.SeleniumChromeLoader import SeleniumChromeLoader
# Typical sites that contain email addresses.
# Everything is lowercase.
potential_sites_en = [
    "impressum", "support", "contact", "imprint", "privacy", "imprint"]
potential_sites_de = ["kontakt", "datenschutz", "über"]
potential_sites_debug = []
potential_sites = set(potential_sites_en +
                      potential_sites_de + potential_sites_debug)

# ignored files
ignore_files = [".exe", ".png", ".pdf", ".jpg"]
ignore_protocols = ["mailto:", "tel:", "javascript:"]

# Header of the crawler.
# Changed the User-Agent to old Mozilla - not everybody likes crawlers.
# currently not used
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}

# enable loader

# choose loader here:
# RequestsLoader - Loads html by just using requests.get
#   (fast but no js and rendering)
# SplashLoader - Loads rendered html by using a dockerized splash-browser
#   (slow but with js and rendering - has a ton of memory leaks)
# SeleniumChromeLoader - Use webdriver and chrome in headless mode
loader = SeleniumChromeLoader

# enabled parsers
# a href="mailto...
# regex for something@something.something
parsers = [MailtoParser, RegexParser]
# --------------------------- Warning! --------------------------
# ----------------- Don't read below this line! -----------------
# ----------------------- Super ugly code! ----------------------


VERBOSE = False


class RESULT_CODES(Enum):
    OK = 1
    SSL_ERROR = 2
    CONNECTION_ERROR = 3
    CONNECTION_TIMEOUT = 4
    UNDEFINED_ERROR = 5


def build_url(baseurl, path):
    # Returns a list in the structure of urlparse.ParseResult
    url_base = urllib.parse.urlparse(baseurl)
    url_new = urllib.parse.urlparse(path)

    if url_new.scheme == "":
        url_new = url_new._replace(scheme=url_base.scheme)
    if url_new.netloc == "":
        url_new = url_new._replace(netloc=url_base.netloc)

    return urllib.parse.urlunparse(url_new)


def get_promising_urls(soup, base):
    global VERBOSE
    global potential_sites
    global ignore_files
    global ignore_protocols

    found_sites = list()
    counter = 0
    soup_links = set(soup.find_all('a', href=True))
    for link in soup_links:
        for site in potential_sites:
            if (link.string is not None and site in link.string.lower()) or site in str(link['href']).lower():
                if link['href'] not in found_sites:
                    if VERBOSE:
                        print("\t\t'found " + site + ": " + str(link['href']))
                    new_link = link['href']

                    ignored = False

                    for p in ignore_protocols:
                        if new_link.lower().strip().startswith(p):
                            ignored = True

                    for i in ignore_files:
                        if new_link.lower().strip().endswith(i) and not ignored:
                            ignored = True

                    if not ignored:
                        check_this_site = build_url(base, new_link)
                        # do not crawl other domains
                        base_domain = tldextract.extract(base).domain
                        check_domain = tldextract.extract(
                            check_this_site).domain
                        if base_domain == check_domain and check_this_site != "":
                            found_sites.append(check_this_site)
    return found_sites


def get_promising_mails(soup):
    global VERBOSE
    global parsers
    email_addresses = set()
    for parser in parsers:
        email_addresses = email_addresses | parser.extract_mail_addresses(
            soup, VERBOSE)

    return email_addresses


def process_url(target):
    global VERBOSE
    global loader

    email_addresses = set()
    links = list()

    try:
        # check for redirects (thanks aok!)
        request = requests.get(target, allow_redirects=True, timeout=10)
        if len(request.history) > 0:
            target = request.url
            if VERBOSE:
                print("Redirected to: " + request.url)
        request.connection.close()
        if VERBOSE:
            print("\nProcessing: " + target)
        soup = loader.load_and_soup(target)
        email_addresses = get_promising_mails(soup)
        links = get_promising_urls(soup, target)
        status = RESULT_CODES.OK
    except requests.exceptions.ConnectionError as e:
        print_exception(target, e, VERBOSE)
        status = RESULT_CODES.CONNECTION_ERROR
    except requests.exceptions.SSLError as e:
        print_exception(target, e, VERBOSE)
        status = RESULT_CODES.SSL_ERROR
    except requests.exceptions.Timeout as e:
        print_exception(target, e, VERBOSE)
        status = RESULT_CODES.CONNECTION_TIMEOUT
    return status, email_addresses, links


def print_exception(target, e, VERBOSE):
    print("Error: " + target + ":")
    print(repr(e).split('(')[0])
    if VERBOSE:
        tb = traceback.format_exc()
        print(tb)
    email_addresses = set()
    links = set()


def strip_emails(results):
    emails = set()
    for email in results:
        if email.startswith("mailto:"):
            emails.add(email[7:])
        elif email.startswith("mailto*"):
            emails.add(email[7:])
        elif email.startswith("regex:"):
            emails.add(email[6:])
        else:
            emails.add(email)
    return emails


def crawl(target, depth, done_urls):
    current_link = target
    emails = set()
    status = RESULT_CODES.OK

    if int(depth) > 0:
        status, new_email_addresses, new_links = process_url(current_link)
        emails = emails.union(set(new_email_addresses))
        done_urls = done_urls.union(set([current_link]))
        if status is not RESULT_CODES.OK:
            return status, set(), set()
        for link in new_links:
            if link not in done_urls:
                status, done_urls, new_emails = crawl(
                    link, int(depth) - 1, done_urls)
                emails = emails.union(new_emails)
                emails = strip_emails(emails)
                if len(emails) > 5:
                    return done_urls, emails
    return status, done_urls, emails


def filter_results_from_regex(emails):
    # filter results for regex errors
    results = []
    for e1 in emails:
        counter = 0
        for e2 in emails:
            if e2.startswith(e1):
                counter += 1
        if counter is 1:
            results.append(e1)
        else:
            if VERBOSE:
                print(e1 + " seems to be an regex related error.")
    return results


def Main():
    global VERBOSE

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "depth", help="Depth of the crawling-prozess. Should not be > 3", type=int)
    parser.add_argument("-u", "--url", help="URL of a site.", type=str)
    parser.add_argument(
        "-l", "--list", help="List of a sites. Should be a PrivacyScore-Export.", type=str)
    parser.add_argument("-v", "--verbose", help="Verbose mode",
                        action="store_true", default=False)
    args = parser.parse_args()

    VERBOSE = args.verbose

    if args.url:
        loader.init()
        status, done_urls, emails = crawl(args.url, args.depth, set())
        if VERBOSE:
            print("\nResult:")

        print(status)
        results = filter_results_from_regex(emails)
        for email in sorted(results):
            print(email)
        loader.cleanup()
    if args.list:
        loader.init()
        VERBOSE = False
        hits = 0
        file = open(args.list, "r")
        text = file.read()
        lines = text.split("\n")
        for i in range(1, len(lines) - 1):
            split_me = lines[i].split(";")
            url = split_me[0]
            status, done_urls, emails = crawl(url, args.depth, set())
            print(str(i) + "/" + str(len(lines) - 2) +
                  "\t" + url + "\t" + str(len(emails)))
            if len(emails) > 0:
                hits += 1
                results = filter_results_from_regex(emails)
                for email in sorted(results):
                    print("\t\t" + email)
            else:
                print("\tNO HITS! TODO!")
        print(str(hits) + " of " + str(len(lines) - 2))
        loader.cleanup()


if __name__ == "__main__":
    Main()
