### WARNING: DEPRECATED!!!
### Solved by executing js

# Searchs for Cloudflare-Protected E-Mail-Addresses.
# Decrypts cloudflares email obfuscation.
# Sources for decryption:
# https://usamaejaz.com/cloudflare-email-decoding/
# http://cryptographybuzz.com/cloudflares-email-address-obfuscation/
# Example Links:
#<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="543931142127353935313e352e7a373b39">[email&#160;protected]</a>
#<a href="/cdn-cgi/l/email-protection#5f323a1f2a2c3e323e3a353e25713c3032"><i class="svg-icon email"></i></a>

from .AbstractBaseClassParser import AbstractBaseClassParser

class CloudflareParser(AbstractBaseClassParser):
    def cf_decode_email(encodedString):
        r = int(encodedString[:2],16)
        email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
        return email

    def extract_mail_addresses(soup, VERBOSE):
        cleartext_emails = set()
        from bs4 import BeautifulSoup, SoupStrainer
        for link in soup.find_all('a', href=True):
            if link['href'].startswith("/cdn-cgi/l/email-protection"):
                if link['href'].startswith("/cdn-cgi/l/email-protection#"):
                    ciphertext = link['href'].split("#")[1]
                else:
                    # todo: untested! could not find a site!
                    ciphertext= link['data-cfemail']
                cleartext = CloudflareParser.cf_decode_email(ciphertext)
                cleartext_emails.add(cleartext.lower().strip())
                if VERBOSE:
                    print("\t\tCloudflareProtection: " + cleartext)
        return cleartext_emails
