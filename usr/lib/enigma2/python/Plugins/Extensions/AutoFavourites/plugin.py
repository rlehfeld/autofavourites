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

from Components.ParentalControl import parentalControl
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.Standby import TryQuitMainloop

APP_NAME 		= 'AutoFavourites'
GEN_FAV_PATH 	= '/usr/lib/enigma2/python/Plugins/Extensions/AutoFavourites/generateFavourites.py'
UPDATE_SAT_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/AutoFavourites/updateSatellites.py'

class AutoFavourites:

	def __init__(self, session):
		self.session = session
		self.global_title = APP_NAME + ' ' + VERSION
		self.menu_options = [
			('Generate Favourites', 'generate'),
			('Update Satellites', 'update'),
			('Exit', 'exit')
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

	def reloadBouquets(self):
		eDVBDB.getInstance().reloadBouquets()

	def reloadBlackList(self):
		parentalControl.open()

	def generateCallback(self):
		self.reloadBouquets()
		self.reloadBlackList()
		self.openMenu()

	def restartInterface(self):
		self.session.open(TryQuitMainloop, 3)

	def updateSatCallback(self):
		self.restartInterface()
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
		if choice is 'generate':

			self.session.openWithCallback(self.generateCallback, Console, title = self.global_title, cmdlist = ['python %s' % GEN_FAV_PATH])
		elif choice is 'update':
			self.session.openWithCallback(self.updateCallback, ChoiceBox, title = self.global_title, list = self.sat_options)
		elif choice is 'exit':
			self.session.close

	def updateSat(self, source):
		self.session.openWithCallback(self.updateSatCallback, Console, title = self.global_title, cmdlist = ['python %s %s' % (UPDATE_SAT_PATH, source)])

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
