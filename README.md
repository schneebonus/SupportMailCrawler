# SupportMailCrawler
Searches popular support sites for support email addresses. For example, the imprint or the contact page will be used.

Do not think about using this project as an email harvester. By using a real browser, the crawler is slow, resource-intensive and poor in scaling.

# Install

Details about dependencies are in install.md.

# Usage:

python3 mail-crawler.py <crawling_depth> --url <target_url>

python3 mail-crawler.py <crawling_depth> --list <list.csv>

Optional: add -v for verbose mode

### Warning: crawling_depth > 3 might take a very long time

### Examples:

python3 mail-crawler.py 2 --url https://privacyscore.org

python3 mail-crawler.py 3 --list lists/InstitutionsOfHigherEducation.csv
