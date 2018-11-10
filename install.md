# Python3 Packages

- re for Regex
- bs4 for HTML-Parsing
- urllib for requests
- tldextract for sub domain parsing

# Requires Splash

Splash is a javascript rendering service with an HTTP API.
It's a lightweight browser with an HTTP API, implemented in Python 3 using Twisted and QT5.
It's fast, lightweight and state-less which makes it easy to distribute.

Link: https://splash.readthedocs.io/en/stable/install.html#linux-docker

### TL;DR:
1. install, enable and start docker
2. sudo docker pull scrapinghub/splash
3. sudo docker run -p 8050:8050 -p 5023:5023 scrapinghub/splash

# Usage:

python3 mail-crawler.py <crawling_depth> -u <target>
  
python3 mail-crawler.py <crawling_depth> -l <list.csv>

Optional: add -v for verbose mode

### Warning: crawling_depth > 3 might take a very long time

### Examples:

python3 mail-crawler.py 2 -u https://privacyscore.org

python3 mail-crawler.py 3 -l lists/InstitutionsOfHigherEducation.csv
