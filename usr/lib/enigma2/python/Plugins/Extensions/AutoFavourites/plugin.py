#################################################################################
#
#    Plugin for Enigma2
#    version:
VERSION = "0.2.1"
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

APP_NAME = "AutoFavourites"
AUTO_FAVOURITES = "python /usr/lib/enigma2/python/Plugins/Extensions/AutoFavourites/autoFavourites.py"

def main(session,**kwargs):
	parts = [
		(_("Automatic scan"), 0, session),
		(_("Add to bouquet"), 1, session),
		(_("Exit"), 2, session)
	]

	text = APP_NAME + " " + VERSION
	session.openWithCallback(menuDone, ChoiceBox, title = text, list = parts)

def menuDone(option):
	if option is None:
		return
	(description, choice, session) = option

	if choice == 0:
		fastScan(session)
	elif choice == 1:
		genFav(session)
	elif choice == 2:
		session.close

def fastScan(session):
	from Screens.ScanSetup import *
	session.open(ScanSimple)

def genFav(session):
	text = APP_NAME
	cmd = AUTO_FAVOURITES
	session.openWithCallback(consoleClosed,Console,text,[cmd])

def consoleClosed(answer=None):
	return

def Plugins(**kwargs):
    return PluginDescriptor(
        name="AutoFavourites",
        description="Generate favourites based on a config file",
        where = PluginDescriptor.WHERE_PLUGINMENU,
        icon="plugin.png",
        fnc=main)
