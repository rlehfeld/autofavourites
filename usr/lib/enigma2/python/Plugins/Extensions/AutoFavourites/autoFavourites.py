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
    regexfav = re.compile(favregexp, re.IGNORECASE)
    channels, namespaces = [], []
    f = open(outdir + '/lamedb').readlines()
    f = f[f.index("services\n")+1:-3]
    while len(f) > 2:
    	serviceref, servicename  = f[0][:-1], f[1][:-1]
        channel = extractchannel(servicename, serviceref)
        if regexfav.match(servicename.strip()):
            if favname.lower() == 'epgrefresh':
                if isepgchannel(channel, namespaces):
                    namespaces.append(channel['NS'])
                    channels.append(channel)
            else:
                channels.append(channel)
        f = f[3:]
    return channels

def writeblacklistfile(favname, favregexp):
    if favname.lower() == 'blacklist':
        blacklistfile = open(outdir + '/blacklist', 'w')
        channels = loadchannels(favname, favregexp)
        writeblacklist(channels, blacklistfile)
        blacklistfile.close()

def writefavfile(favname, favregexp):
    if not favname.lower() in ['blacklist']:
        favfile = open(outdir + '/' + genfavfilename(favname), 'w')
        favfile.write('#NAME %s\n' % favname)
        channels = loadchannels(favname, favregexp)
        writechannels(channels, favfile)
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
