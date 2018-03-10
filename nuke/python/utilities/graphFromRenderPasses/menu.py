import nuke
import PySide.QtGui
import nukeGraph as ng

nuke.menu("Nuke").addCommand("Utilities/Create Graph from Render Passes", "ng.generateNukeScript()")
