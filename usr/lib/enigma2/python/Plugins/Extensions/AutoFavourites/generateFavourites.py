OUT_DIR#!/usr/bin/python

import os
import glob
import re
import unicodedata

#	SID:NS:TSID:ONID:STYPE:UNUSED(channelnumber in enigma1)
#	X   X  X    X    D     D

#	REFTYPE:FLAGS:STYPE:SID:TSID:ONID:NS:PARENT_SID:PARENT_TSID:UNUSED
#   D       D     X     X   X    X    X  X          X           X

#---------------------------------------------
OUT_DIR = '/etc/enigma2'
RULES_CONF  = '/etc/bouquetRules.cfg'
#---------------------------------------------

def removeoldfiles():
    userbouquets = glob.glob(OUT_DIR + '/userbouquet.*')
    for userbouquet in userbouquets:
        os.remove(userbouquet)

    bouquetindexes = glob.glob(OUT_DIR + '/bouquets.*')
    for bouquetindex in bouquetindexes:
        os.remove(bouquetindex)

    blacklists = glob.glob(OUT_DIR + '/blacklist')
    for blacklist in blacklists:
        os.remove(blacklist)

def genfavfilename(name):
    name = unicodedata.normalize('NFKD', unicode(name, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
    name = re.sub('[^a-z0-9]', '', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
    return 'userbouquet.%s.tv' % name

def createtvindex():
    favindexfile = open(OUT_DIR + '/bouquets.tv', 'w')
    favindexfile.write('#NAME User - bouquets (TV)\n')

    filerules = open(RULES_CONF)
    for rule in filerules:
        favname ,__ ,__ = rule.split(':')
        favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % genfavfilename(favname))
    filerules.close()

    favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet\n')
    favindexfile.close()

def createradioindex():
    radioindexfile = open(OUT_DIR + '/bouquets.radio', 'w')
    radioindexfile.write('#NAME User - bouquets (RADIO)\n')
    radioindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet\n')
    radioindexfile.close()

def genfavindex():
    createtvindex()
    createradioindex()

def extracttransp(serviceref):
    f = open(OUT_DIR + '/lamedb').readlines()
    f = f[f.index("transponders\n")+1:-3]
    while (f and f[0][:3] != 'end'):
        transpid, transpref = f[0][:-1], f[1][:-1]
        if serviceref[5:23] == transpid:
            ttype, tref = transpref.strip().split(' ')
            return [ttype, tref.split(':')]
        f = f[3:]
    raise Exception('Transponder not found!')

def extractservice(serviceref, servicename):
    ref = serviceref.split(':')
    return { 'name': servicename, 'sid': ref[0], 'ns': ref[1], 'tsid': ref[2], 'onid': ref[3], 'stype': int(ref[4]) }

def writeservices(services, file):
    services = sorted(services, key=lambda service: service['name'].lower())
    for service in services:
        file.write('#SERVICE 1:0:%(stype)x:%(sid)s:%(tsid)s:%(onid)s:%(ns)s:0:0:0\n' % service)

def writeblacklist(services, file):
    for service in services:
        file.write('1:0:%(stype)x:%(sid)s:%(tsid)s:%(onid)s:%(ns)s:0:0:0\n' % service)

def isepgservice(service, namespaces):
    istvservice = service['stype'] in [1, 19]
    isuniquens  = (not (service['ns'] in namespaces))
    return (istvservice and isuniquens)

def loadservices(favname, satpos, favregexp):
    regexfav = re.compile(favregexp, re.IGNORECASE)
    services, namespaces = [], []
    f = open(OUT_DIR + '/lamedb').readlines()
    f = f[f.index("services\n")+1:-3]
    while f and f[0][:3] != 'end':
    	serviceref, servicename  = f[0][:-1], f[1][:-1]
        service                  = extractservice(serviceref, servicename)
        __, transp               = extracttransp(serviceref)
        issatposmatch            = satpos in ['000', transp[4]]
        isservicenamematch       = regexfav.match(servicename.strip())
        if issatposmatch and isservicenamematch:
            if favname.lower() == 'epgrefresh':
                if isepgservice(service, namespaces):
                    namespaces.append(service['ns'])
                    services.append(service)
            else:
                services.append(service)
        f = f[3:]
    return services

def writeblacklistfile(favname, satpos, favregexp):
    blistfile = open(OUT_DIR + '/blacklist', 'w')
    services = loadservices(favname, satpos, favregexp)
    writeblacklist(services, blistfile)
    blistfile.close()

def writefavfile(favname, satpos, favregexp):
    favfile = open(OUT_DIR + '/' + genfavfilename(favname), 'w')
    favfile.write('#NAME %s\n' % favname)
    services = loadservices(favname, satpos, favregexp)
    writeservices(services, favfile)
    favfile.close()

def genblacklist():
    filerules = open(RULES_CONF)
    for rline in filerules:
        favname, satpos, favregexp = rline.split(':')
        if favname.lower() == 'blacklist':
            writeblacklistfile(favname, satpos, favregexp)
    filerules.close()

def genfav():
    filerules = open(RULES_CONF)
    for rline in filerules:
        favname, satpos, favregexp = rline.split(':')
        if favname.lower() != 'blacklist':
            writefavfile(favname, satpos, favregexp)
    filerules.close()

def gendefaultfav():
    favtvallfile = open(OUT_DIR + '/userbouquet.favourites.tv', 'w')
    favtvallfile.write('#NAME Favourites (TV)\n')
    favtvallfile.close()

    favradioallfile = open(OUT_DIR + '/userbouquet.favourites.radio', 'w')
    favradioallfile.write('#NAME Favourites (Radio)\n')
    favradioallfile.close()

def main():
    print('Removing old files...')
    removeoldfiles()
    print('Generating favourites index...')
    genfavindex()
    print('Generating default favourites...')
    gendefaultfav()
    print('Generating favourites...')
    genfav()
    print('Generating blacklist...')
    genblacklist()

main()
