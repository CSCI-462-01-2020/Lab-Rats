#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Cell Management.
#
# Cell Management is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cell Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cell Management.  If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pygame
import sugargame
import sugargame.canvas
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import StopButton
from gettext import gettext as _
import cells

class Activity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.max_participants = 1
        self.game = cells.Game()
        self.game.canvas = sugargame.canvas.PygameCanvas(
            self,
            main=self.game.mainloop,
            modules=[pygame.display, pygame.font])
        self.set_canvas(self.game.canvas)
        self.game.canvas.grab_focus()
        self.build_toolbar()

    def build_toolbar(self):
        
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>q'
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.show_all()

    def read_file(self, file_path):
        pass
        
    def write_file(self, file_path):
        pass

