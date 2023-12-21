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

#   service types:
#   ==============
#   type 1 = digital television service
#   type 2 = digital radio sound service
#   type 4 = nvod reference service (NYI)
#   type 10 = advanced codec digital radio sound service
#   type 17 = MPEG-2 HD digital television service
#   type 22 = advanced codec SD digital television
#   type 24 = advanced codec SD NVOD reference service (NYI)
#   type 25 = advanced codec HD digital television
#   type 27 = advanced codec HD NVOD reference service (NYI)
#   type 31 = UHD

#   service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 31) || (type == 134) || (type == 195)'
#   service_types_radio = '1:7:2:0:0:0:0:0:0:0:(type == 2) || (type == 10)'

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

                # radio service types
                self._rules.setdefault('radio', [2, 10])

                # tv service types
                self._rules.setdefault('tv', [1, 17, 22, 25, 31, 135, 195])

                for rule in self._rules.get('rules', []):
                    rule['mode'] = rule.get('mode', 'tv').lower()

                    for station in rule.get('stations', []):
                        for key in ('sid', 'ns', 'tsid', 'onid', 'stype'):
                            for k in (key, '!' + key):
                                if k in station:
                                    station[k] = toint(station[k])

                        station.setdefault('stype', self._rules[rule['mode']])

        except (OSError, IOError):
            self._rules = {}

    def get_rules(self):
        return self._rules.get('rules', [])

    def get_service_types(mode):
        return self._rules['mode']

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
                'name': re.sub(r'[^\w\s{}()\[\]+\-.]', '', servicename),
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
    name = re.sub(r'[^a-z0-9]+', '_', name.replace('&', 'and').replace('/', 'and').replace('+', 'plus').replace('*', 'star').lower())
    mode = rule['mode']
    return 'userbouquet.autofav-%s.%s' % (name, mode.lower())

def createindex(mode):
    bouquetindex = 'bouquets.%s' % mode
    services = []
    with io.open(os.path.join(CONFIG.out_dir, bouquetindex), 'r', encoding='utf8') as favindexfile:
        for line in favindexfile:
            if line.startswith('#SERVICE ') and -1 == line.find('"userbouquet.autofav-'):
                services.append(line.rstrip('\r\n'))

    bouquettype = 'TV' if mode.lower() == 'tv' else 'Radio'
    rules = CONFIG.get_rules()
    prefix = '#SERVICE 1:7:%i:0:0:0:0:0:0:0' % (1 if mode == 'tv' else 2)

    with io.open(os.path.join(CONFIG.out_dir, bouquetindex), 'w', encoding='utf8') as favindexfile:
        print(u'#NAME User - bouquets (%s)' % bouquettype, file=favindexfile)
        for service in services:
            print(service, file=favindexfile)

        for rule in rules:
            if rule['mode'] == mode:
                print(
                    u'%s:FROM BOUQUET "%s" ORDER BY bouquet' % (prefix, genfavfilename(rule)),
                    file=favindexfile
                )

def tohex(value):
    if isinstance(value, list):
        return [tohex(v) for v in value]
    if isinstance(value, dict):
        return {k: tohex(v) for k, v in value.items()}
    if value is not True and value is not False and isinstance(value, int):
        return '%x' % value
    return value

def toint(value):
    if isinstance(value, list):
        return [toint(v) for v in value]
    if isinstance(value, dict):
        return {k: toint(v) for k, v in value.items()}
    if value is not True and value is not False and not isinstance(value, int):
        return int(value, 16)
    return value

def genfavindex():
    createindex('tv')
    createindex('radio')

def isepgservice(service, transponders, transponder):
    istvservice = service['stype'] in CONFIG.get_service_types('tv')
    isunique = (not (transponder in transponders))
    return (istvservice and isunique)

def includes(stationvalue, servicevalue):
    if isinstance(servicevalue, list):
        if isinstance(stationvalue, list):
            return bool(set(servicevalue) & set(stationvalue))
        return stationvalue in servicevalue

    if isinstance(stationvalue, list):
        return servicevalue in stationvalue
    return stationvalue == servicevalue

def true(_):
    return True

def false(_):
    return False

def toregexp(value, default):
    if value is None:
        return default
    if isinstance(value, list):
        value = '|'.join(map(lambda p: '(?:%s)' % p,  value))
    return re.compile(value, re.U).search

def integer(value):
    try:
        return int(value)
    except ValueError:
        return value

class Tuple(tuple):
    def __new__(self, *args):
        return tuple.__new__(Tuple, tuple(*args))

    def __lt__(self, other):
        for k, v in zip(self, other):
            if k != v:
                if isinstance(k, type(v)):
                    return k < v
                if not isinstance(k, int):
                    return True
                return False
        return False

def splitchannel(service):
    channel = service['name'].lower()
    split = list(re.findall(r'[^\d\s]+|\d+', re.sub(r'[^\w\s]', '', channel)))
    split.append(channel)
    t = Tuple(integer(t) for t in split)
    return t

def loadservices(rule):
    allservices = []
    transponders = []

    print('Parsing %s...' % rule['name'])
    for station in rule['stations']:
        services = []
        regexfav = toregexp(station.get('regexp', None), true)
        notregexfav = toregexp(station.get('!regexp', None), false)

        for service in CONFIG.get_services():
            if (not any(includes(station['!' + key], service[key])
                        for key in service if ('!' + key) in station) and
                    all(includes(station[key], service[key])
                        for key in service if key in station)):
                if not notregexfav(service['name']) and regexfav(service['name']):
                    if rule['name'] == 'epgrefresh':
                        transponder = '%(ns)08X:%(tsid)04X:%(onid)04X' % service
                        if not isepgservice(service, transponders, transponser):
                            continue
                        transponders.append(transponder)
                        addservice = service.copy()
                    else:
                        # TODO: add this to epgrefresh bouquet automatically
                        addservice = service.copy()
                        addservice['icam'] = station.get('icam', False)

                    addservice.update(
                        {
                            'reftype': 1,
                        }
                    )
                    addservice.update(station.get('replace', {}))
                    services.append(addservice)

        for service in sorted(services, key=splitchannel):
            if service not in allservices:
                if rule.get('keepduplicates', False) or service['name'] not in (s['name'] for s in allservices):
                    if rule.get('debug', False):
                        print('Added %s' % tohex(service))
                    allservices.append(service)
                elif rule.get('debug', False):
                    print('Skipping %s as channel name already existing.' % tohex(service))

    return allservices

def writefavfile(rule):
    with io.open(os.path.join(CONFIG.out_dir, genfavfilename(rule)), 'w', encoding='utf8') as favfile:
        print(u'#NAME %s' % rule['name'], file=favfile)
        for service in loadservices(rule):
            if service.get('icam', False):
                url = CONFIG.get_icamprefix() + u'/%(reftype)d:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:%(ns)X:0:0:0:' % service
                serviceinfo = u'#SERVICE %(reftype)d:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:21:0:0:0' % service
                print(u'%s:%s:%s' % (serviceinfo, url.replace(':', '%3a'), service['name']), file=favfile)
                print(u'#DESCRIPTION %s' % service['name'], file=favfile)
            else:
                url = service.get('url')
                servicestr = u'#SERVICE %(reftype)d:0:%(stype)X:%(sid)X:%(tsid)X:%(onid)X:%(ns)X:0:0:0:' % service
                if url is not None:
                    servicestr += url.replace(':', '%3a') + ':%(name)s' % service
                print(servicestr, file=favfile)

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
