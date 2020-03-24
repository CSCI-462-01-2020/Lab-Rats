#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# pieces.py is part of Cells. Cells is free software: you can 
# redistribute it and/or modify it under the terms of the GNU 
# General Public License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
#
# Cells is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cells.  If not, see <http://www.gnu.org/licenses/>.

import pygame
from sprites import Group, Text, Prisoner
from colors import red, green, black, white

################################################################################
# The Cells
################################################################################

class Cell():
    def __init__(self, game, species):
        self.game = game
        self.species = species
    
    def isSelected(self):
        m = pygame.mouse.get_pos()
        d = self.game.dist(m[0], m[1], self.x, self.y)
        if d < 54:
            return True
   
    def seti(self, i):
        self.i = i

    def setPos(self, x, y):
        self.x = x
        self.y = y

        pygame.draw.circle(self.game.background, black, (x, y), 54)
        pygame.draw.circle(self.game.background, white, (x, y), 50)

        text = Text(str(self.species + 1), size = 20)
        text.rect.center = (self.x, self.y - 20)
        self.text = Group((text))

    def makePrisoners(self):
        self.prisoners = Group()
        self.prisoners.set_pos(self.x, self.y)
        self.prisoner1 = Prisoner(self.game, self.species, self.x, self.y, 'left')
        self.prisoner2 = Prisoner(self.game, self.species, self.x, self.y, 'right')
        self.prisoners.add((self.prisoner1, self.prisoner2))
    
    def reset(self):
        self.prisoner1.kill()
        self.prisoner2.kill()
        self.prisoners.add((self.prisoner1, self.prisoner2))

    def setMyHS(self, hs):
        self.my_hs = hs

    def getMyHS(self):
        return self.my_hs

    def setAdjHS(self, hs):
        self.adj_hs = hs

    def getAdjHS(self):
        return self.adj_hs
    
    def addPrisoner(self, prisoner):
        self.prisoners.add(prisoner)

    def update(self):
        if (len(self.prisoners) != 0 and
            self.getAdjHS().canHelp()):
            prisoner = self.prisoners.sprites()[0]
            self.prisoners.remove(prisoner)
            self.getMyHS().addPrisoner(prisoner)

################################################################################
# The Escape Area
################################################################################
        
class EscapeArea():
    def __init__(self, game):
        self.game = game
        self.prisoners = Group()
        self.prisoners.set_pos(600,450)
        
    def addPrisoner(self, prisoner):
        self.prisoners.add(prisoner)

################################################################################
# The Hideout
################################################################################
           
class Hideout():
    def __init__(self, game, species, cell, HorF):
        self.game = game
        self.species = species
        self.my_cell = cell
        self.HorF = HorF
        self.prisoners = Group()
        self.escArea = game.escArea

    def seti(self, int):
        self.i = int

    def setPos(self, x, y):
        self.x = x
        self.y = y
        self.prisoners.set_pos(self.x, self.y)

        # since we're at it, let's use our crayon to color on the board
        # this is so we can tell if a space is 'hostile' or 'friendly'
        color = red
        if self.HorF == "f":
            color = green
        pygame.draw.circle(self.game.background, black, (x,y), 54)
        pygame.draw.circle(self.game.background, color, (x,y), 50)

        text = Text(str(self.species + 1), size = 20, color = white)
        text.rect.center = (self.x, self.y - 20)
        self.text = Group((text))
        
    def isOccupied(self):
        if len(self.prisoners.sprites()) == 0:
            return False
        return True
    
    def vacate(self):
        if self.isOccupied():
            x = self.prisoners.sprites()[0]
            self.prisoners.remove(x)
            self.my_cell.prisoners.add(x)
            
    def canHelp(self):
        return ((self.isOccupied() and self.HorF == "f") or
                (not self.isOccupied() and self.HorF == "h"))
            
    def escape(self, prisoner):
        self.escArea.addPrisoner(prisoner)

    def addPrisoner(self, prisoner):
        if not self.isOccupied():
            self.prisoners.add((prisoner))
        else:
            self.escape(prisoner)

