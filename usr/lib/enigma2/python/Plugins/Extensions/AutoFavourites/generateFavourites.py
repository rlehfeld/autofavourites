#!/usr/bin/python

#	SID:NS:TSID:ONID:STYPE:UNUSED(channelnumber in enigma1)
#	X   X  X    X    D     D

#	REFTYPE:FLAGS:STYPE:SID:TSID:ONID:NS:PARENT_SID:PARENT_TSID:UNUSED
#   D       D     X     X   X    X    X  X          X           X

import os
import glob
import re
import unicodedata

OUT_DIR = '/etc/enigma2'
RULES_CONF  = '/etc/bouquetRules.cfg'

def removeoldfiles():
    userbouquets = glob.glob(OUT_DIR + '/userbouquet.*')
    for userbouquet in userbouquets:
        os.remove(userbouquet)

    bouquetindexes = glob.glob(OUT_DIR + '/bouquets.*')
    for bouquetindex in bouquetindexes:
        os.remove(bouquetindex)

def genfavfilename(name):
    name = unicodedata.normalize('NFKD', unicode(name, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
    name = re.sub('[^a-z0-9]', '', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
    return 'userbouquet.%s.tv' % name

def createtvindex():
    favindexfile = open(OUT_DIR + '/bouquets.tv', 'w')
    favindexfile.write('#NAME User - bouquets (TV)\n')
    filerules = open(RULES_CONF)
    for rline in filerules:
        favname ,__ = rline[:-1].split(':')
        favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % genfavfilename(favname))
    filerules.close()
    favindexfile.close()

def createradioindex():
    radioindexfile = open(OUT_DIR + '/bouquets.radio', 'w')
    radioindexfile.write('#NAME User - bouquets (RADIO)\n')
    radioindexfile.close()

def genfavindex():
    createtvindex()
    createradioindex()

def extractservice(serviceref, servicename):
    ref = serviceref.split(':')
    return { 'name': servicename, 'sid': ref[0], 'ns': ref[1], 'tsid': ref[2], 'onid': ref[3], 'stype': int(ref[4]) }

def isepgservice(service, transponders):
    transponder = ":".join([service['ns'], service['tsid'],service['onid']])
    istvservice = service['stype'] in [1, 25]
    isunique = (not (transponder in transponders))
    return (istvservice and isunique)

def loadservices(favname, favregexp):
    regexfav = re.compile(favregexp, re.IGNORECASE)
    services, transponders = [], []
    f = open(OUT_DIR + '/lamedb').readlines()
    f = f[f.index("services\n")+1:-3]
    while f and f[0][:3] != 'end':
    	serviceref, servicename  = f[0][:-1], f[1][:-1]
        service = extractservice(serviceref, servicename)
        transponder = ":".join([service['ns'], service['tsid'], service['onid']])
        if regexfav.search(servicename):
            if favname.lower() == 'epgrefresh':
                if isepgservice(service, transponders):
                    transponders.append(transponder)
                    services.append(service)
            else:
                services.append(service)
        f = f[3:]
    return services

def writefavfile(favname, favregexp):
    favfile = open(OUT_DIR + '/' + genfavfilename(favname), 'w')
    favfile.write('#NAME %s\n' % favname)
    services = loadservices(favname, favregexp)
    services = sorted(services, key=lambda service: service['name'].lower())
    for service in services:
        favfile.write('#SERVICE 1:0:%(stype)x:%(sid)s:%(tsid)s:%(onid)s:%(ns)s:0:0:0\n' % service)
    favfile.close()

def genfav():
    filerules = open(RULES_CONF)
    for rline in filerules:
        favname, favregexp = rline[:-1].split(':')
        writefavfile(favname, favregexp)
    filerules.close()

def main():
    print('Removing old files...')
    removeoldfiles()
    print('Generating favourites index...')
    genfavindex()
    print('Generating favourites...')
    genfav()

main()
