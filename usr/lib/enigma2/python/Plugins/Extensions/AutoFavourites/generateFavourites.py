#!/usr/bin/python

#	SID:NS:TSID:ONID:STYPE:UNUSED(channelnumber in enigma1)
#	X   X  X    X    D     D

#	REFTYPE:FLAGS:STYPE:SID:TSID:ONID:NS:PARENT_SID:PARENT_TSID:UNUSED
#   D       D     X     X   X    X    X  X          X           X

import os
import sys
import glob
import re
import json
import unicodedata

class config:
    def __init__(self, prefix=os.sep):
        self.prefix = prefix

    @property
    def out_dir(self):
        return os.path.join(self._prefix, 'etc', 'enigma2')

    @property
    def rules_conf(self):
        return os.path.join(self._prefix, 'etc', 'enigma2', 'bouquetRules.json')

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = os.path.expanduser(value)

    def parse_rules(self):
        self._rules = []
        try:
            with open(self.rules_conf) as filerules:
                self._rules = json.load(filerules)
        except FileNotFoundError:
            pass

    def get_rules(self):
        return self._rules

    def has_rules(self):
        return bool(self.get_rules())

    def parse_services(self):
        with open(os.path.join(CONFIG.out_dir, 'lamedb')) as lamedb:
            f = lamedb.readlines()

        f = f[f.index("services\n")+1:-3]

        self._services = []
        while f and f[0][:3] != 'end':
            serviceref, servicename  = f[0][:-1], f[1][:-1]
            self._services.append(self._extractservice(serviceref, servicename))
            f = f[3:]

    def get_services(self):
        return self._services

    @staticmethod
    def _extractservice(serviceref, servicename):
        ref = serviceref.split(':')
        return {
            'name': servicename,
            'sid': ref[0],
            'ns': ref[1],
            'tsid': ref[2],
            'onid': ref[3],
            'stype': int(ref[4])
        }

CONFIG = config()

def removeoldfiles():
    userbouquets = glob.glob(os.path.join(CONFIG.out_dir, 'userbouquet.*'))
    for userbouquet in userbouquets:
        os.remove(userbouquet)

    bouquetindexes = glob.glob(os.path.join(CONFIG.out_dir, 'bouquets.*'))
    for bouquetindex in bouquetindexes:
        os.remove(bouquetindex)

def genfavfilename(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = re.sub('[^a-z0-9]', '', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
    return 'userbouquet.%s.tv' % name

def createtvindex():
    with open(os.path.join(CONFIG.out_dir, 'bouquets.tv'), 'w') as favindexfile:
        favindexfile.write('#NAME User - bouquets (TV)\n')
        rules = CONFIG.get_rules
        for rule in rules:
            favindexfile.write(
                '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % genfavfilename(rule['name'])
            )

def createradioindex():
    with open(os.path.join(CONFIG.out_dir, 'bouquets.radio'), 'w') as radioindexfile:
        radioindexfile.write('#NAME User - bouquets (RADIO)\n')

def genfavindex():
    createtvindex()
    createradioindex()

def isepgservice(service, transponders, transponder):
    istvservice = service['stype'] in [1, 25]
    isunique = (not (transponder in transponders))
    return (istvservice and isunique)

def loadservices(rule):
    allservices = []
    transponders = []

    for station in rule['stations']:
        services = []
        regexfav = re.compile(station['regexp']) if 'regexp' in station else None

        for service in CONFIG.get_services():
            if all(service[key] == station[key] for key in service.keys() if key in station.keys()):
                if regexfav is None or regexfav.search(service['name']):
                    if rule['name'] == 'epgrefresh':
                        transponder = ':'.join([service['ns'], service['tsid'], service['onid']])
                        if isepgservice(service, transponders, transponser):
                            transponders.append(transponder)
                            services.append(service)
                    else:
                        services.append(service)
        allservices.extend(sorted(services, key=lambda service: service['name'].lower()))

    return allservices

def writefavfile(rule):
    with open(os.path.join(CONFIG.out_dir, genfavfilename(rule['name'])), 'w') as favfile:
        favfile.write('#NAME %s\n' % rule['name'])
        for service in loadservices(rule):
            favfile.write('#SERVICE 1:0:%(stype)x:%(sid)s:%(tsid)s:%(onid)s:%(ns)s:0:0:0\n' % service)

def genfav():
    rules = CONFIG.get_rules()
    for rule in rules:
        writefavfile(rule)

def main():
    print('Parsing rules config...')
    CONFIG.parse_rules()
    if CONFIG.has_rules():
        # TODO: remove debug print
        print(CONFIG.get_rules())
        print('Parsing available services...')
        CONFIG.parse_services()
        #print('Removing old files...')
        #removeoldfiles()
        #print('Generating favourites index...')
        #genfavindex()
        print('Generating favourites...')
        genfav()
    else:
        print('Missing rules config. Skip generating Favourites')

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        CONFIG.prefix = sys.argv[1]
    main()
