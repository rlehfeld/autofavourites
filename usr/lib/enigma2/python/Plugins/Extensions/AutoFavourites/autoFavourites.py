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
outdir    = '/etc/enigma2'
rules     = '/etc/bouquetRules.cfg'
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
        if favname.lower() != 'blacklist':
            favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % genfavfilename(favname))

    favindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet\n')
    favindexfile.close()

    radioindexfile = open(outdir + '/bouquets.radio', 'w')
    radioindexfile.write('#NAME User - bouquets (RADIO)\n')
    radioindexfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet\n')
    radioindexfile.close()

def extractchannel(name, serviceref):
    ref = serviceref.split(':')
    return { 'NAME': name, 'SID': ref[0], 'NS': ref[1], 'TSID': ref[2], 'ONID': ref[3], 'STYPE': int(ref[4]) }

def writechannels(channels, file):
    channels = sorted(channels, key=lambda channel: channel['NAME'].lower())
    for channel in channels:
        file.write('#SERVICE 1:0:%(STYPE)x:%(SID)s:%(TSID)s:%(ONID)s:%(NS)s:0:0:0\n' % channel)

def writeblacklist(channels, file):
    for channel in channels:
        file.write('1:0:%(STYPE)x:%(SID)s:%(TSID)s:%(ONID)s:%(NS)s:0:0:0\n' % channel)

def isepgchannel(channel, namespaces):
    istvchannel = channel['STYPE'] in [1, 19]
    isuniquens  = (not (channel['NS'] in namespaces))
    return (istvchannel and isuniquens)

def loadchannels(favname, favregexp):
    channels, namespaces = [], []
    serviceref, servicesreading = None, False
    regexref = re.compile('^.{4}:.{8}:.{4}:.{4}')
    regexfav = re.compile(favregexp, re.IGNORECASE)

    filelamedb = open(outdir + '/lamedb')
    for line in filelamedb:
        if line.strip() == 'services':
            servicesreading = True
            continue
        if servicesreading:
            if line.strip() == 'end':
                servicesreading = False
                continue
            if line.strip().startswith('p:'):
                continue
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
    return channels

def genblacklist():
    filerules = open(rules)
    for rline in filerules:
        favname, favregexp = extractrule(rline)
        if favname.lower() == 'blacklist':
            blacklistfile = open(outdir + '/blacklist', 'w')
            channels = loadchannels(favname, favregexp)
            writeblacklist(channels, blacklistfile)
            blacklistfile.close()
    filerules.close()

def genfav():
    filerules = open(rules)
    for rline in filerules:
        favname, favregexp = extractrule(rline)
        if favname.lower() != 'blacklist':
            favfile = open(outdir + '/' + genfavfilename(favname), 'w')
            favfile.write('#NAME %s\n' % favname)
            channels = loadchannels(favname, favregexp)
            writechannels(channels, favfile)
            favfile.close()
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
