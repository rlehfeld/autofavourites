#!/usr/bin/python

import os
import glob
import re
import unicodedata

#	SID:NS:TSID:ONID:STYPE:UNUSED(channelnumber in enigma1)
#	X   X  X    X    D     D

#	REFTYPE:FLAGS:STYPE:SID:TSID:ONID:NS:PARENT_SID:PARENT_TSID:UNUSED
#   D       D     X     X   X    X    X  X          X           X

#---------------------------------------------
outdir = '/etc/enigma2'
rules  = '/etc/bouquetRules.cfg'
#---------------------------------------------

def removeoldfiles():
    userbouquets = glob.glob(outdir + '/userbouquet.*')
    for userbouquet in userbouquets:
        os.remove(userbouquet)

    bouquetindexes = glob.glob(outdir + '/bouquets.*')
    for bouquetindex in bouquetindexes:
        os.remove(bouquetindex)

    blacklists = glob.glob(outdir + '/blacklist')
    for blacklist in blacklists:
        os.remove(blacklist)

def genfavfilename(name):
    name = unicodedata.normalize('NFKD', unicode(name, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
    name = re.sub('[^a-z0-9]', '', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
    return 'userbouquet.%s.tv' % name

def extractrule(rule):
    return rule.strip().split(':')

def createtvindex():
    favindexfile = open(outdir + '/bouquets.tv', 'w')
    favindexfile.write('#NAME User - bouquets (TV)\n')

    filerules = open(rules)
    for rule in filerules:
        favname, favregexp = extractrule(rule)
        if not favname.lower() in ['blacklist']:
            favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % genfavfilename(favname))

    favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet\n')
    favindexfile.close()

def createradioindex():
    radioindexfile = open(outdir + '/bouquets.radio', 'w')
    radioindexfile.write('#NAME User - bouquets (RADIO)\n')
    radioindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet\n')
    radioindexfile.close()

def genfavindex():
    createtvindex()
    createradioindex()

def extractservice(name, serviceref):
    ref = serviceref.split(':')
    return { 'NAME': name, 'SID': ref[0], 'NS': ref[1], 'TSID': ref[2], 'ONID': ref[3], 'STYPE': int(ref[4]) }

def writeservices(services, file):
    services = sorted(services, key=lambda service: service['NAME'].lower())
    for service in services:
        file.write('#SERVICE 1:0:%(STYPE)x:%(SID)s:%(TSID)s:%(ONID)s:%(NS)s:0:0:0\n' % service)

def writeblacklist(services, file):
    for service in services:
        file.write('1:0:%(STYPE)x:%(SID)s:%(TSID)s:%(ONID)s:%(NS)s:0:0:0\n' % service)

def isepgservice(service, namespaces):
    istvservice = service['STYPE'] in [1, 19]
    isuniquens  = (not (service['NS'] in namespaces))
    return (istvservice and isuniquens)

def loadservices(favname, favregexp):
    regexfav = re.compile(favregexp, re.IGNORECASE)
    services, namespaces = [], []
    f = open(outdir + '/lamedb').readlines()
    f = f[f.index("services\n")+1:-3]
    while len(f) > 2:
    	serviceref, servicename  = f[0][:-1], f[1][:-1]
        service = extractservice(servicename, serviceref)
        if regexfav.match(servicename.strip()):
            if favname.lower() == 'epgrefresh':
                if isepgservice(service, namespaces):
                    namespaces.append(service['NS'])
                    services.append(service)
            else:
                services.append(service)
        f = f[3:]
    return services

def writeblacklistfile(favname, favregexp):
    if favname.lower() == 'blacklist':
        blacklistfile = open(outdir + '/blacklist', 'w')
        services = loadservices(favname, favregexp)
        writeblacklist(services, blacklistfile)
        blacklistfile.close()

def writefavfile(favname, favregexp):
    if not favname.lower() in ['blacklist']:
        favfile = open(outdir + '/' + genfavfilename(favname), 'w')
        favfile.write('#NAME %s\n' % favname)
        services = loadservices(favname, favregexp)
        writeservices(services, favfile)
        favfile.close()

def genblacklist():
    filerules = open(rules)
    for rline in filerules:
        favname, favregexp = extractrule(rline)
        writeblacklistfile(favname, favregexp)
    filerules.close()

def genfav():
    filerules = open(rules)
    for rline in filerules:
        favname, favregexp = extractrule(rline)
        writefavfile(favname, favregexp)
    filerules.close()

def gendefaultfav():
    favtvallfile = open(outdir + '/userbouquet.favourites.tv', 'w')
    favtvallfile.write('#NAME Favourites (TV)\n')
    favtvallfile.close()

    favradioallfile = open(outdir + '/userbouquet.favourites.radio', 'w')
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
