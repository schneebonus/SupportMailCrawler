# Parses for a href="mailto:..."
from bs4 import BeautifulSoup, SoupStrainer
import re
from .AbstractBaseClassParser import AbstractBaseClassParser

class UnCryptMailtoParser(AbstractBaseClassParser):
    def guess_encryption(s):
        decryptionModules = [BkkDecrypt, UnivativDecrypt]
        for decryptionModule in decryptionModules:
            result = decryptionModule.UnCryptMailto(s)
            if result.startswith("mailto"):
                return result.lower().strip()
        else:
            return None

    def extract_mail_addresses(soup, VERBOSE):
        emails = set()
        for link in soup.find_all('a', href=True):
            if link['href'].startswith("javascript:linkTo_UnCryptMailto"):
                m = re.search('^javascript:linkTo_UnCryptMailto\(\'(.+?)\'\);$', link['href'])
                if m:
                    secret = m.group(1)
                else:
                    secret = ""
                guess = UnCryptMailtoParser.guess_encryption(secret)
                if guess is not None:
                    # ToDo: why do I need replace?
                    # Is there a problem in my decryption?
                    emails.add(guess.replace("[.",".").replace("`", "z").lower())
                    if VERBOSE:
                        print("\t\tUnCryptMailtoParser: " + guess)
        return emails

# Seems to be the default-way to encrypt
# Tutorials:
# https://jumk.de/nospam/
# https://www.math.uni-hamburg.de/it/dienste/encryptma.html
# http://www.derwok.de/service/email_stopspam/
# Examples:
# http://www.bkk-bpw.de/
class BkkDecrypt:
    def UnCryptMailto(s):
        n = 0
        r = ""
        for i in range(0,len(s)):
            n=ord(s[i]) # char code
            if n > 8364:
                n = 128
            n_minus_1 = n - 1
            r += chr(n_minus_1) # string from char code
        return r

# Another decryption
# Examples
# https://univativ.com
class UnivativDecrypt:
    def decryptCharcode(n, start, end, offset):
        n = n + offset
        if offset > 0 and n > end:
            n = start + (n - end - 1);
        elif offset < 0 and n < start:
            n = end - (start - n - 1);
        return chr(n)

    def decryptString(enc, offset):
        dec = ""
        for i in range(0, len(enc)):
            n = ord(enc[i])
            if n >= 43 and n <= 58:
                # 0-9 . , - + / :
                dec += UnivativDecrypt.decryptCharcode(n, 43, 58, offset)
            elif n >= 64 and n <= 90:
                # A-Z @
                dec += UnivativDecrypt.decryptCharcode(n, 64, 90, offset)
            elif n >= 97 and n <= 122:
                # a-z
                dec += UnivativDecrypt.decryptCharcode(n, 97, 112, offset)
            else:
                dec += enc[i]
        return dec

    def UnCryptMailto(s):
        for i in range(-10, 10, 1):
            result = UnivativDecrypt.decryptString(s, i).lower()
            if result.startswith("mailto"):
                return result.lower()
        return "not found"
