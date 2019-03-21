#!/usr/bin/python

import os
import sys
import glob
import re
import unicodedata

#	SID:NS:TSID:ONID:STYPE:UNUSED(channelnumber in enigma1)
#	X   X  X    X    D     D

#	REFTYPE:FLAGS:STYPE:SID:TSID:ONID:NS:PARENT_SID:PARENT_TSID:UNUSED
#   D       D     X     X   X    X    X  X          X           X

#---------------------------------------------
lamedb = '/etc/enigma2/lamedb'
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

def genfavfilename(name):
    name = unicode(name.replace(' ', '').lower(), 'UTF-8')
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return 'userbouquet.%s.tv' % name

def extractrule(rule):
    return rule.strip().split(':')

def genfavindex():
    favindexfile = open(outdir + '/bouquets.tv', 'w')
    favindexfile.write('#NAME User - bouquets (TV)\n')

    filerules = open(rules)
    for rule in filerules:
        favname, favregexp = extractrule(rule)
        favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % genfavfilename(favname))

    favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet\n')
    favindexfile.close()

    radioindexfile = open(outdir + '/bouquets.radio', 'w')
    radioindexfile.write('#NAME User - bouquets (RADIO)\n')
    radioindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet\n')
    radioindexfile.close()

def extractchannel(name, serviceref):
    serv = serviceref.split(':')
    return { 'NAME': name, 'SID': serv[0], 'NS': serv[1], 'TSID': serv[2], 'ONID': serv[3], 'STYPE': serv[4] }

def writechannels(channels, favfile):
    channels = sorted(channels, key=lambda channel: channel['NAME'].lower())
    for channel in channels:
        favfile.write('#SERVICE 1:0:%(STYPE)s:%(SID)s:%(TSID)s:%(ONID)s:%(NS)s:0:0:0\n' % channel)

def isepgchannel(channel, namespaces):
    istvchannel = channel['STYPE'] in ('1', '25') # SD/HD
    isuniquens  = (not (channel['NS'] in namespaces))
    return (istvchannel and isuniquens)

def genfav():
    filerules = open(rules)
    for rline in filerules:
        favname, favregexp = extractrule(rline)
        favfile = open(outdir + '/' + genfavfilename(favname), 'w')
        favfile.write('#NAME %s\n' % favname)

        regexref = re.compile('^.{4}:.{8}:.{4}:.{4}:.{1}:.{1}:.{1}$')
        regexfav = re.compile(favregexp, re.IGNORECASE)
        channels, namespaces = [], []
        serviceref, servicesreading = None, False
        filelamedb = open(lamedb)
        for line in filelamedb:
            if line.strip() == 'services':
                servicesreading = True
                continue
            if servicesreading and line.strip() == 'end':
                servicesreading = False
                continue
            if servicesreading:
                if regexref.match(line.strip()):
                    serviceref = line.strip()
                    continue
                if regexfav.match(line.strip()):
                    channel = extractchannel(line.strip(), serviceref)
                    if favname.lower() == 'epgrefresh':
                        if isepgchannel(channel, namespaces):
                            namespaces.append(channel['NS'])
                            channels.append(channel)
                    else:
                        channels.append(channel)

        filelamedb.close()

        writechannels(channels, favfile)
        favfile.close()

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

main()
