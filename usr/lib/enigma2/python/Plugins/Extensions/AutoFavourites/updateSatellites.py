#!/usr/bin/python

import os
import sys
import urllib

#---------------------------------------------
URL_SOURCE_1 = "http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml"
URL_SOURCE_2 = "http://satbr.herokuapp.com/satellites/source1.xml"
URL_SOURCE_3 = "http://satbr.herokuapp.com/satellites/source2.xml"
OUT_DIR = "/etc/enigma2/satellites.xml"
#OUT_DIR = "satellites.xml"
#---------------------------------------------

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def main():
    choice = str(sys.argv[1])
    log('Downloading satellites.xml...\n')
    if choice is "1":
        urllib.urlretrieve(URL_SOURCE_1, OUT_DIR)
    elif choice is "2":
        urllib.urlretrieve(URL_SOURCE_2, OUT_DIR)
    elif choice is "3":
        urllib.urlretrieve(URL_SOURCE_3, OUT_DIR)




main()
