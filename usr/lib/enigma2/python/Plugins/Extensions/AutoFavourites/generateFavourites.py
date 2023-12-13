#!/usr/bin/python

#   SID:NS:TSID:ONID:STYPE:UNUSED(channelnumber in enigma1)
#   X   X  X    X    D     D

#   REFTYPE:FLAGS:STYPE:SID:TSID:ONID:NS:PARENT_SID:PARENT_TSID:UNUSED
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
                for rule in self._rules:
                    for station in rule['stations']:
                        if 'ns' in station:
                            station['ns'] = int(station['ns'], 16)
        except FileNotFoundError:
            pass

    def get_rules(self):
        return self._rules

    def has_rules(self):
        return bool(self.get_rules())

    def parse_services(self):
        with open(os.path.join(CONFIG.out_dir, 'lamedb')) as lamedb:
            f = lamedb.readlines()

        f = f[f.index("services\n")+1:-1]

        self._services = []
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
    name = re.sub('[^a-z0-9]+', '_', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
    mode = rule.get('mode', 'tv')
    return 'userbouquet.autofav-%s.%s' % (name, mode.lower())

def createindex(mode):
    bouquetindex = 'bouquets.%s' % mode
    services = []
    with open(os.path.join(CONFIG.out_dir, bouquetindex), 'r') as favindexfile:
        for line in favindexfile:
            if line.startswith('#SERVICE ') and -1 == line.find('"userbouquet.autofav-'):
                services.append(line)

    bouquettype = 'TV' if mode.lower() == 'tv' else 'Radio'
    rules = CONFIG.get_rules()
    prefix = '#SERVICE 1:7:%i:0:0:0:0:0:0:0' % (1 if mode == 'tv' else 2)

    with open(os.path.join(CONFIG.out_dir, bouquetindex), 'w') as favindexfile:
        favindexfile.write('#NAME User - bouquets (%s)\n' % bouquettype)
        for service in services:
            favindexfile.write(service)

        for rule in rules:
            if rule.get('mode', 'tv').lower() == mode:
                favindexfile.write(
                    '%s:FROM BOUQUET "%s" ORDER BY bouquet\n' % (prefix, genfavfilename(rule))
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
        regexfav = re.compile(station['regexp']) if 'regexp' in station else None

        for service in CONFIG.get_services():
            if all(includes(station[key], service[key])
                   for key in service.keys() if key in station.keys()):
                if regexfav is None or regexfav.search(service['name']):
                    if rule['name'] == 'epgrefresh':
                        transponder = ':'.join([service['ns'], service['tsid'], service['onid']])
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
    with open(os.path.join(CONFIG.out_dir, genfavfilename(rule)), 'w') as favfile:
        favfile.write('#NAME %s\n' % rule['name'])
        for service in loadservices(rule):
            if service.get('icam', False):
                description = re.sub('[^a-zA-Z0-9 ]', '', service['name'])
                url = 'http%%3a//127.0.0.1%%3a17999/1%%3a0%%3a%(stype)X%%3a%(sid)X%%3a%(tsid)X%%3a%(onid)X%%3a%(ns)X%%3a0%%3a0%%3a0%%3a' % service
                serviceinfo = '#SERVICE 1:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:21:0:0:0' % service
                favfile.write('%s:%s:%s\n' % (serviceinfo, url, description))
                favfile.write('#DESCRIPTION %s\n' % description)
            else:
                favfile.write('#SERVICE 1:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:%(ns)X:0:0:0\n' % service)

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
