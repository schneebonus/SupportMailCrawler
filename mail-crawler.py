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
import signal
import sys
import urllib.request
import time
from parsers.RegexParser import RegexParser
from parsers.MailtoParser import MailtoParser
from loaders.SeleniumChromeLoader import SeleniumChromeLoader
from utils.TLDCheck import TLDCheck
# Typical sites that contain email addresses.
# Everything is lowercase.
potential_sites_en = [
    "impressum", "support", "contact", "imprint",
    "privacy", "publisher"]
potential_sites_de = ["kontakt", "datenschutz", "ansprechpartner"]
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
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64)' +
    ' AppleWebKit/537.36 (KHTML, like Gecko) ' +
    'Chrome/70.0.3538.77 Safari/537.36'
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
# MailtoParser
parsers = [RegexParser]

# check tlds
check = TLDCheck()

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
    SITE_NOT_FOUND = 6


def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Cleaning chrome...')
    loader.cleanup()
    sys.exit(0)


def build_url(baseurl, path):
    # Returns a list in the structure of urlparse.ParseResult
    url_new = urllib.parse.urlparse(path)

    # todo: base html tag!

    if url_new.scheme == "":
        path = urllib.parse.urljoin(baseurl, path)

    return path


def get_promising_urls(soup, base):
    global VERBOSE
    global potential_sites
    global ignore_files
    global ignore_protocols

    found_sites = set()
    soup_links = set(soup.find_all('a', href=True))
    for link in soup_links:
        for site in potential_sites:
            if ((link.string is not None and
                    site in link.string.lower()) or
                    site in str(link['href']).lower()):
                if VERBOSE:
                    print("\t\t'found " + site + ": " + str(link['href']))
                new_link = link['href']

                ignored = False

                for p in ignore_protocols:
                    if new_link.lower().strip().startswith(p):
                        ignored = True

                for i in ignore_files:
                    if (new_link.lower().strip().endswith(i) and
                            not ignored):
                        ignored = True

                if not ignored:
                    check_this_site = build_url(base, new_link)
                    # do not crawl other domains
                    if is_in_scope(base, check_this_site):
                        found_sites.add(check_this_site)
    return found_sites


def get_promising_mails(soup):
    global VERBOSE
    global parsers
    global check
    email_addresses = set()
    for parser in parsers:
        email_addresses = email_addresses | parser.extract_mail_addresses(
            soup, VERBOSE, check)

    return email_addresses


def is_in_scope(scope, url):
    base_domain = tldextract.extract(scope).domain
    check_domain = tldextract.extract(url).domain
    return base_domain == check_domain


def inspect_frames(target, soup):
    # ToDo:
    # crawl for frames and add content to links
    frames = set()
    soup_frames = soup.find_all('frame')
    for fr in soup_frames:
        if fr.has_attr('src'):
            real_location = build_url(target, fr['src'])
            if is_in_scope(target, real_location):
                frames.add((real_location))
    soup_iframes = soup.find_all('iframe')
    for fr in soup_iframes:
        if fr.has_attr('src'):
            real_location = build_url(target, fr['src'])
            if is_in_scope(target, real_location):
                frames.add((real_location))
    return frames


def process_url(target, blacklist):
    global VERBOSE
    global loader

    email_addresses = set()
    links = list()
    if VERBOSE:
        print("\nProcessing: " + target)
    target = loader.navigate_to_url(target)
    if target not in blacklist:
        soup = loader.load_and_soup(target)
        if site_found(soup):
            email_addresses = get_promising_mails(soup)
            links = get_promising_urls(soup, target)
            frames = inspect_frames(target, soup)
            blacklist.add(target)
            for frame in frames:
                if frame not in blacklist:
                    status, done_urls, new_emails = crawl(frame, 1, blacklist)
                    email_addresses = email_addresses.union(new_emails)
                    blacklist = blacklist.union(done_urls)
            status = RESULT_CODES.OK
        else:
            status = RESULT_CODES.SITE_NOT_FOUND
    else:
        status = RESULT_CODES.OK
    return blacklist, status, email_addresses, links


def site_found(soup):
    if soup.text.strip() == "":
        return False
    return True


def crawl(target, depth, done_urls):
    emails = set()
    status = RESULT_CODES.OK

    if int(depth) > 0:
        done_url_p, status, new_email_addresses, new_links = process_url(
            target, done_urls)
        emails = emails.union(set(new_email_addresses))

        # in case of a redirect:
        # add both links!
        done_urls = done_urls.union(done_url_p)
        done_urls.add(target)
        if status is not RESULT_CODES.OK:
            return status, set(), set()
        for link in new_links:
            if link not in done_urls:
                # if len(emails) > 10:
                #    depth = 1
                # ToDo: clicked links might break the recursion!
                status, done_urls, new_emails = crawl(
                    link, int(depth) - 1, done_urls)
                emails = emails.union(new_emails)
    return status, done_urls, emails


def Main():
    global VERBOSE
    global check

    check.init()
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "depth",
        help="Depth of the crawling-prozess. Should not be > 3",
        type=int)
    parser.add_argument("-u", "--url",
                        help="URL of a site.",
                        type=str)
    parser.add_argument(
        "-l", "--list",
        help="List of a sites. Should be a PrivacyScore-Export.",
        type=str)
    parser.add_argument(
        "-t", "--test",
        help="Test against a file. File should use this format: url;email",
        type=str)
    parser.add_argument("-v", "--verbose",
                        help="Verbose mode",
                        action="store_true",
                        default=False)
    args = parser.parse_args()

    VERBOSE = args.verbose

    if args.url:
        loader.init()
        loader.navigate_to_url(args.url)
        print(loader.current_url())
        status, done_urls, emails = crawl(args.url, args.depth, set())
        print(status)
        results = emails
        for email in sorted(results):
            print(email)
        loader.cleanup()
    if args.test:
        start = time.time()
        loader.init()
        VERBOSE = 0

        match = 0
        no_results = 0
        connection_errors = 0
        found_different = 0
        testset_had_none_but_crawler = 0
        true_negatives = 0

        tested = 0

        file = open(args.test, "r")
        text = file.read()
        lines = text.split("\n")

        for i in range(0, len(lines) - 1):
            split_me = lines[i].split(";")
            url = split_me[0]
            email = split_me[1]
            tested += 1
            loader.navigate_to_url(url)
            status, done_urls, emails = crawl(url, args.depth, set())
            if status is RESULT_CODES.OK:
                if email.lower() in emails:
                    match += 1
                    print("+\t" + str(
                        tested) +
                        "/" + str(len(lines[:-1]))
                        + "\t" + url
                        + ": true positive")
                elif len(emails) is 0:
                    if email != "\\N":
                        no_results += 1
                        print("-\t" + str(
                            tested) +
                            "/" + str(len(lines[:-1])) +
                            "\t" + url +
                            ": false negative: could not finde " + email)
                    else:
                        print("+\t" + str(
                            tested) +
                            "/" + str(len(lines[:-1])) +
                            "\t" + url +
                            ": true negative")
                        true_negatives += 1
                else:
                    if email != "\\N":
                        found_different += 1
                        print("~\t" + str(
                            tested) +
                            "/" + str(len(lines[:-1])) +
                            "\t" + url + ": found " + str(len(emails)) +
                            " addresses but not " + email)
                        for email in emails:
                            print("\t\t" + email)
                    else:
                        testset_had_none_but_crawler += 1
                        print("~\t" + str(
                            tested) + "/" +
                            str(len(lines[:-1])) + "\t" + url +
                            ": found " + str(len(emails)) +
                            " address but the testset had none.")
                        for email in emails:
                            print("\t\t" + email)
            else:
                connection_errors += 1
                print("-\t" + str(
                    tested) + "/" + str(len(lines[:-1])) + "\t" +
                    url + ": EXCEPTION: " + str(status))
        end = time.time()
        print("\nResult:\n")
        print("Datei: " + args.test + "\n")
        print("Erledigt " + str(tested) + " URLs")
        print("")
        print("| Rating | Class | Amount |")
        print("|:-----------|:---------------|----------:|")
        print("| Positiv | Adresse aus dem Testset gefunden | " + str(match) + " |")
        print("| | Testset hatte keine Adresse und es wurde keine gefunden | " +
              str(true_negatives) + " |")
        print("| | Testset hatte keine Adresse aber es wurde etwas gefunden¹ | " +
              str(testset_had_none_but_crawler) + "|")
        print("| | Summe | " + str(match + true_negatives
                                   + testset_had_none_but_crawler) + " |")
        print("| Neutral | Testset hatte eine Adresse aber statt dieser Adresse wurde etwas anderes gefunden² | " +
              str(found_different) + " |")
        print("| | Exceptions | " + str(connection_errors) + " |")
        print("| | Summe| " + str(found_different + connection_errors) + " |")
        print("| Negative | Testset hatte eine Adresse aber es wurde nichts gefunden | " +
              str(no_results) + " |")
        print("| | Summe | " + str(no_results) + " |")
        print("")
        print("Laufzeit: " + '{:5.3f}s'.format(end - start))
        print("¹ Treffer können sinnvoll aber auch unbrauchbar sein. Da das Testset hier keinen Vergleichswert hat, ist keine automatisierte Aussage möglich.")
        print("² Es ist möglich, dass eine neuere Adresse gefunden wurde. Es ist aber auch möglich, dass statt der richtigen Adresse etwas komplett unbrauchbares erfasst wurde. Da das Testset hier keinen Vergleichswert hat, ist keine automatisierte Aussage möglich.")
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
            loader.navigate_to_url(url)
            status, done_urls, emails = crawl(url, args.depth, set())
            print(str(i) + "/" + str(len(lines) - 2) +
                  "\t" + url + "\t" + str(len(emails)))
            if len(emails) > 0:
                hits += 1
                results = emails
                for email in sorted(results):
                    print("\t\t" + email)
            else:
                print("\tNO HITS! TODO!")
        print(str(hits) + " of " + str(len(lines) - 2))
        loader.cleanup()


if __name__ == "__main__":
    Main()
