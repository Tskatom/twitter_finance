#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
from bs4 import BeautifulSoup
import urllib2
import codecs
import chardet


def get_english(en_url):
    try:
        req = urllib2.urlopen(en_url)
        raw = req.read()
        encoding = chardet.detect(raw)['encoding']
        content = unicode(raw, encoding)
        soup = BeautifulSoup(content)
        p = soup.find("p", "colortermino")
        if p is None:
            return None
        text = p.parent.parent.nextSibling.next.text
        en_val = text.replace(".\
            ", "").encode("utf-8").lower()
        return en_val
    except KeyboardInterrupt:
        print "Error %s %s" % (en_url, sys.exc_info()[0])
        raise
    except:
        print "--------Error ---%s %s" % (en_url, sys.exc_info()[0])
    return None


def extract_finance_terms(url):
    try:
        req = urllib2.urlopen(url)
        raw = req.read()
        encoding = chardet.detect(raw)['encoding']
        content = unicode(raw, encoding)
        soup = BeautifulSoup(content)
        h3s = soup.find_all("h3")
        terms = {}
        i = 0
        for h3 in h3s:
            i += 1
            try:
                href = h3.a['href']
                text = h3.a.text
                term = text.encode('utf-8').lower()
                #get the english value
                en_url = urllib2.urlparse.urljoin(url, href)
                en_value = get_english(en_url)
                terms[term] = en_value
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                print "%s Exception for :" % sys.exc_info()[0], h3, "-", text
                raise
        return terms
    except KeyboardInterrupt:
        print "Exception %s " % sys.exc_info()[0]
        raise KeyboardInterrupt
    except:
        print "Exception %s" % sys.exc_info()[0]


def brower_website(finance_dic_file):
    orgin_url = 'http://www.spanish-translator-services.com/'
    orgin_url += 'espanol/diccionarios/finanzas-espanol-ingles/'
    w = codecs.open(finance_dic_file, "w")
    for i in range(ord('a'), ord('v') + 1):
        c = chr(i)
        r_url = "%s%s/" % (orgin_url, c)
        print r_url
        try:
            terms = extract_finance_terms(r_url)
            if terms is not None:
                for term, en_value in terms.items():
                    w.write("%s|%s\n" % (term, en_value))
        except KeyboardInterrupt:
            print "Interrupt by keyboard"
            w.flush()
            break
        w.flush()
    w.close()


def main():
    fin_file = sys.argv[1]
    brower_website(fin_file)


if __name__ == "__main__":
    main()
