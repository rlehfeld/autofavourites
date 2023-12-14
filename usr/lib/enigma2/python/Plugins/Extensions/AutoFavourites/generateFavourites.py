#!/usr/bin/python

#   lamedb transponders:
#   ====================
#   NS:TSID:ONID
#   X  X    X
#   DVBType Frequenz:SymbolRate:Polarisation:FEC:SatPosition:Inversion ???????
#   [cts]   D        D          D            D   D           D

#   lamedb services:
#   ================
#   SID:NS:TSID:ONID:STYPE:UNUSED(channelnumber in enigma1)
#   X   X  X    X    D     D

#   bouquet files:
#   ==============
#   REFTYPE:FLAGS:STYPE:SID:TSID:ONID:NS:PARENT_SID:PARENT_TSID:UNUSED
#   D       D     X     X   X    X    X  X          X           X

from __future__ import print_function

import os
import io
import sys
import glob
import re
import json
import unicodedata

class config(object):
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
        try:
            with io.open(self.rules_conf, encoding='utf8') as filerules:
                self._rules = json.load(filerules)
                for rule in self._rules.get('rules', []):
                    for station in rule.get('stations', []):
                        if 'ns' in station:
                            station['ns'] = int(station['ns'], 16)
        except (OSError, IOError):
            self._rules = {}

    def get_rules(self):
        return self._rules.get('rules', [])

    def has_rules(self):
        return bool(self.get_rules())

    def get_icamprefix(self):
        return self._rules.get('icam', u'http://127.0.0.1:17999')

    def parse_services(self):
        databases = glob.glob(
            os.path.join(CONFIG.out_dir, self._rules.get('database', 'lamedb'))
        )

        self._services = []

        for database in databases:
            with io.open(database, encoding='utf8') as lamedb:
                f = lamedb.readlines()

            f = f[f.index("services\n")+1:-1]

            while f and f[0].rstrip('\r\n') != 'end':
                serviceref, servicename, serviceinfo = (
                    f[0].rstrip('\r\n'),
                    f[1].rstrip('\r\n'),
                    f[2].rstrip('\r\n')
                )

                self._services.append(
                    self._extractservice(
                        serviceref,
                        servicename,
                        serviceinfo,
                    )
                )
                f = f[3:]

    def get_services(self):
        return self._services

    @staticmethod
    def _extractservice(serviceref, servicename, serviceinfo):
        ref = serviceref.split(':')
        info = serviceinfo.split(',')

        kv = {}

        for i in info:
            k, v = i.split(':', 2)
            if k not in kv:
                kv[k] = []
            kv[k].append(v)

        kv.update(
            {
                'name': servicename,
                'sid': int(ref[0], 16),
                'ns': int(ref[1], 16),
                'tsid': int(ref[2], 16),
                'onid': int(ref[3], 16),
                'stype': int(ref[4], 10)
            }
        )
        return kv

CONFIG = config()

def removeoldfiles():
    userbouquets = glob.glob(os.path.join(CONFIG.out_dir, 'userbouquet.autofav-*.tv'))
    for userbouquet in userbouquets:
        print('Removing %s' % userbouquet)
        os.remove(userbouquet)

def genfavfilename(rule):
    name = unicodedata.normalize('NFKD', rule['name']).encode('ASCII', 'ignore').decode('utf-8')
    name = re.sub(r'[^a-z0-9]+', '_', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
    mode = rule.get('mode', 'tv')
    return 'userbouquet.autofav-%s.%s' % (name, mode.lower())

def createindex(mode):
    bouquetindex = 'bouquets.%s' % mode
    services = []
    with io.open(os.path.join(CONFIG.out_dir, bouquetindex), 'r', encoding='utf8') as favindexfile:
        for line in favindexfile:
            if line.startswith('#SERVICE ') and -1 == line.find('"userbouquet.autofav-'):
                services.append(line)

    bouquettype = 'TV' if mode.lower() == 'tv' else 'Radio'
    rules = CONFIG.get_rules()
    prefix = '#SERVICE 1:7:%i:0:0:0:0:0:0:0' % (1 if mode == 'tv' else 2)

    with io.open(os.path.join(CONFIG.out_dir, bouquetindex), 'w', encoding='utf8') as favindexfile:
        print(u'#NAME User - bouquets (%s)' % bouquettype, file=favindexfile)
        for service in services:
            print(service, file=favindexfile)

        for rule in rules:
            if rule.get('mode', 'tv').lower() == mode:
                print(
                    u'%s:FROM BOUQUET "%s" ORDER BY bouquet' % (prefix, genfavfilename(rule)),
                    file=favindexfile
                )

def genfavindex():
    createindex('tv')
    createindex('radio')

def isepgservice(service, transponders, transponder):
    istvservice = service['stype'] in [1, 25]
    isunique = (not (transponder in transponders))
    return (istvservice and isunique)

def includes(stationvalue, servicevalue):
    if stationvalue == servicevalue:
        return True
    if not isinstance(servicevalue, list):
        return False
    if isinstance(stationvalue, list):
        return bool(set(servicevalue) & set(stationvalue))
    return stationvalue in servicevalue

def loadservices(rule):
    allservices = []
    transponders = []

    for station in rule['stations']:
        services = []
        regexfav = re.compile(station['regexp'], re.U) if 'regexp' in station else None

        for service in CONFIG.get_services():
            if (not any(includes(station['!' + key], service[key])
                                 for key in service.keys() if ('!' + key) in station.keys()) and
                    all(includes(station[key], service[key])
                        for key in service.keys() if key in station.keys())):
                if regexfav is None or regexfav.search(service['name']):
                    if rule['name'] == 'epgrefresh':
                        transponder = '%(ns)08X:%(tsid)04X:%(onid)04X' % service
                        if isepgservice(service, transponders, transponser):
                            transponders.append(transponder)
                            services.append(service)
                    else:
                        addservice = service.copy()
                        addservice['icam'] = station.get('icam', False)
                        services.append(addservice)

        for service in sorted(services, key=lambda service: service['name'].lower()):
            if service not in allservices:
                allservices.append(service)

    return allservices

def writefavfile(rule):
    with io.open(os.path.join(CONFIG.out_dir, genfavfilename(rule)), 'w', encoding='utf8') as favfile:
        print(u'#NAME %s' % rule['name'], file=favfile)
        for service in loadservices(rule):
            if service.get('icam', False):
                description = re.sub(r'[^a-zA-Z0-9 ]', '', service['name'])
                url = CONFIG.get_icamprefix() + u'/1:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:%(ns)X:0:0:0:' % service
                serviceinfo = u'#SERVICE 1:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:21:0:0:0' % service
                print(u'%s:%s:%s' % (serviceinfo, url.replace(':', '%3a'), description), file=favfile)
                print(u'#DESCRIPTION %s' % description, file=favfile)
            else:
                print(u'#SERVICE 1:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:%(ns)X:0:0:0:' % service, file=favfile)

def genfav():
    rules = CONFIG.get_rules()
    for rule in rules:
        writefavfile(rule)

def main():
    print('Parsing rules config...')
    CONFIG.parse_rules()
    if CONFIG.has_rules():
        print('Parsing available services...')
        CONFIG.parse_services()
        print('Removing old files...')
        removeoldfiles()
        print('Generating favourites index...')
        genfavindex()
        print('Generating favourites...')
        genfav()
    else:
        print('Missing rules config. Skip generating Favourites')

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        CONFIG.prefix = sys.argv[1]
    main()
