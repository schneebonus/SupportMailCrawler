# SupportMailCrawler
Searches popular support sites for support email addresses. For example, the imprint or the contact page will be used.

# Install

Details about dependencies are in install.md.

# Usage:

python3 mail-crawler.py <crawling_depth> -u <target>
  
python3 mail-crawler.py <crawling_depth> -l <list.csv>

Optional: add -v for verbose mode

### Warning: crawling_depth > 3 might take a very long time

### Examples:

python3 mail-crawler.py 2 --url https://privacyscore.org

python3 mail-crawler.py 3 --list lists/InstitutionsOfHigherEducation.csv
