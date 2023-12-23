#!/usr/bin/python

import os
import sys
import urllib, ssl

#---------------------------------------------
URL_ALLIANCE  = 'http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml'
URL_OPENPLI   = 'http://raw.githubusercontent.com/OpenPLi/tuxbox-xml/master/xml/satellites.xml'
URL_PORTALEDS = 'http://raw.githubusercontent.com/lazaronixon/autofavourites_satellites/master/portal_eds/satellites.xml'
URL_PORTALBSD = 'https://raw.githubusercontent.com/lazaronixon/autofavourites_satellites/master/portal_bsd/satellites.xml'
OUT_DIR       = '/etc/enigma2/satellites.xml'
#---------------------------------------------

def main():
    print('Downloading satellites.xml...')
    choice = str(sys.argv[1])
    if choice == 'alliance':
        urllib.urlretrieve(URL_ALLIANCE, OUT_DIR, context=ssl._create_unverified_context())
    elif choice == 'openpli':
        urllib.urlretrieve(URL_OPENPLI, OUT_DIR, context=ssl._create_unverified_context())
    elif choice == 'portaleds':
        urllib.urlretrieve(URL_PORTALEDS, OUT_DIR, context=ssl._create_unverified_context())
    elif choice == 'portalbsd':
        urllib.urlretrieve(URL_PORTALBSD, OUT_DIR, context=ssl._create_unverified_context())

main()
