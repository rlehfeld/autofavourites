#################################################################################
#
#    Plugin for Enigma2
#    version:
VERSION = "0.2.5"
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

from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop

APP_NAME = "AutoFavourites"
AUTO_FAVOURITES = "python /usr/lib/enigma2/python/Plugins/Extensions/AutoFavourites/autoFavourites.py"
UPDATE_SATELLITE = "python /usr/lib/enigma2/python/Plugins/Extensions/AutoFavourites/updateSatellites.py"

class AutoFavourites:

	def __init__(self, session):
		self.session = session
		self.global_title = APP_NAME + " " + VERSION
		self.menu_options = [
			(_("Automatic scan"), "scan"),
			(_("Add to bouquet"), "generate"),
			(_("Update") + " satellite.xml", "update"),
			(_("Exit"), "exit")
		]
		self.sat_options = [
			("OE-Alliance", "source1"),
			("OpenPli", "source2"),
			("Portal EDS", "source3"),
			("Portal BSD", "source4")
		]
		self.openMenu()

	def openMenu(self):
		self.session.openWithCallback(self.menuDone, ChoiceBox, title = self.global_title, list = self.menu_options)

	def menuDone(self, option):
		if option is None:
			return

		(description, choice) = option
		if choice is "scan":
			self.fastScan()
		elif choice is "generate":
			self.genFav()
		elif choice is "update":
			self.session.openWithCallback(self.menuDoneSat, ChoiceBox, title = self.global_title, list = self.sat_options)
		elif choice is "exit":
			self.session.close

	def menuDoneSat(self, option):
		if option is None:
			self.openMenu()
			return

		(description, choice) = option
		if choice is "source1":
			self.updateSat('1')
		elif choice is "source2":
			self.updateSat('2')
		elif choice is "source3":
			self.updateSat('3')
		elif choice is "source4":
			self.updateSat('4')

	def fastScan(self):
		from Screens.ScanSetup import *
		self.session.openWithCallback(self.openMenu, ScanSimple)

	def genFav(self):
		self.session.openWithCallback(self.openMenu, Console, self.global_title, [AUTO_FAVOURITES])

	def updateSat(self, source):
		self.session.openWithCallback(self.restartGUI, Console, self.global_title, [UPDATE_SATELLITE + " " + source])

	def restartGUI(self):
		self.session.open(TryQuitMainloop, 3)
		return False

###############################################################################
def main(session, **kwargs):
	AutoFavourites(session)

###############################################################################

def Plugins(**kwargs):
    return PluginDescriptor(
        name="AutoFavourites",
        description="Generate favourites based on a config file",
        where = PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main)
