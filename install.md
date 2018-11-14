# Python3 Packages

- re for Regex
- bs4 for HTML-Parsing
- urllib for requests
- tldextract for sub domain parsing

# Requires Chrome and Chrome Driver

- Install Chrome for your distribution
- Install Chrome Driver to ""/usr/bin/chromedrive"
  - ToDO: Should be something like:
      - wget chromedriver
      - unzip chromedriver.zip
      - sudo cp chromedriver /usr/bin

# Usage:

python3 mail-crawler.py <crawling_depth> --url <target_url>

python3 mail-crawler.py <crawling_depth> --list <list.csv>

Optional: add -v for verbose mode

### Warning: crawling_depth > 3 might take a very long time

### Examples:

python3 mail-crawler.py 2 -u https://privacyscore.org

python3 mail-crawler.py 3 -l lists/InstitutionsOfHigherEducation.csv
