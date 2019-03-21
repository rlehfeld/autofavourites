#!/usr/bin/python

import os
import sys
import urllib, ssl

#---------------------------------------------
URL_SOURCE_1 = 'http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml'
URL_SOURCE_2 = 'http://raw.githubusercontent.com/OpenPLi/tuxbox-xml/master/xml/satellites.xml'
URL_SOURCE_3 = 'http://satbr.herokuapp.com/satellites/source1.xml'
URL_SOURCE_4 = 'http://satbr.herokuapp.com/satellites/source2.xml'
OUT_DIR      = '/etc/enigma2/satellites.xml'
#---------------------------------------------

def main():
    print('Downloading satellites.xml...')
    choice = str(sys.argv[1])
    if choice is '1':
        urllib.urlretrieve(URL_SOURCE_1, OUT_DIR, context=ssl._create_unverified_context())
    elif choice is '2':
        urllib.urlretrieve(URL_SOURCE_2, OUT_DIR, context=ssl._create_unverified_context())
    elif choice is '3':
        urllib.urlretrieve(URL_SOURCE_3, OUT_DIR, context=ssl._create_unverified_context())
    elif choice is '4':
        urllib.urlretrieve(URL_SOURCE_4, OUT_DIR, context=ssl._create_unverified_context())

main()
