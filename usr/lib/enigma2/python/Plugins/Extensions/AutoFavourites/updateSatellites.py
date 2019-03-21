#!/usr/bin/python

import os
import sys
import urllib, ssl

#---------------------------------------------
URL_ALLIANCE  = 'http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml'
URL_OPENPLI   = 'http://raw.githubusercontent.com/OpenPLi/tuxbox-xml/master/xml/satellites.xml'
URL_PORTALEDS = 'http://satbr.herokuapp.com/satellites/source1.xml'
URL_PORTALBSD = 'http://satbr.herokuapp.com/satellites/source2.xml'
OUT_DIR       = '/etc/enigma2/satellites.xml'
#---------------------------------------------

def main():
    print('Downloading satellites.xml...')
    choice = str(sys.argv[1])
    if choice is 'alliance':
        urllib.urlretrieve(URL_ALLIANCE, OUT_DIR, context=ssl._create_unverified_context())
    elif choice is 'openpli':
        urllib.urlretrieve(URL_OPENPLI, OUT_DIR, context=ssl._create_unverified_context())
    elif choice is 'portaleds':
        urllib.urlretrieve(URL_PORTALEDS, OUT_DIR, context=ssl._create_unverified_context())
    elif choice is 'portalbsd':
        urllib.urlretrieve(URL_PORTALBSD, OUT_DIR, context=ssl._create_unverified_context())

main()
