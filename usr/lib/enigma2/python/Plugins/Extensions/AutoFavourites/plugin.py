#################################################################################
#
#    Plugin for Enigma2
#    version:
VERSION = '0.2.5'
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#################################################################################

from enigma import eDVBDB

from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.Standby import TryQuitMainloop
from Screens.ScanSetup import *

APP_NAME = 'AutoFavourites'

class AutoFavourites:

	def __init__(self, session):
		self.session = session
		self.global_title = APP_NAME + ' ' + VERSION
		self.menu_options = [
			(_('Automatic scan'), 'scan'),
			(_('Add to bouquet'), 'generate'),
			(_('Update') + ' satellite.xml', 'update'),
			(_('Exit'), 'exit')
		]
		self.sat_options = [
			('OE-Alliance', 'alliance'),
			('OpenPli', 'openpli'),
			('Portal EDS', 'portaleds'),
			('Portal BSD', 'portalbsd')
		]
		self.openMenu()

	def openMenu(self):
		self.session.openWithCallback(self.menuDone, ChoiceBox, title = self.global_title, list = self.menu_options)

	def generateCallback(self):
		eDVBDB.getInstance().reloadBouquets()
		self.openMenu()

	def updateSatCallback(self):
		self.session.open(TryQuitMainloop, 3)
		return False

	def updateCallback(self, option):
		if option is None:
			self.openMenu()
		else:
			self.updateSat(option[1])

	def menuDone(self, option):
		if option is None:
			return False

		(description, choice) = option
		if choice is 'scan':
			self.session.openWithCallback(self.openMenu, ScanSimple)
		elif choice is 'generate':
			cmd = ['python /usr/lib/enigma2/python/Plugins/Extensions/AutoFavourites/autoFavourites.py']
			self.session.openWithCallback(self.generateCallback, Console, title = self.global_title, cmdlist = cmd)
		elif choice is 'update':
			self.session.openWithCallback(self.updateCallback, ChoiceBox, title = self.global_title, list = self.sat_options)
		elif choice is 'exit':
			self.session.close

	def updateSat(self, source):
		cmd = ['python /usr/lib/enigma2/python/Plugins/Extensions/AutoFavourites/updateSatellites.py' + ' ' + source]
		self.session.openWithCallback(self.updateSatCallback, Console, title = self.global_title, cmdlist = cmd)

###############################################################################
def main(session, **kwargs):
	AutoFavourites(session)

###############################################################################

def Plugins(**kwargs):
    return PluginDescriptor(
        name='AutoFavourites',
        description='Generate favourites based on a config file',
        where = PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main)
