#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# 'Cells' writen by Nolan Baker - September 18, 2008
# based on the logic puzzle 'Cell Management' by Dr. Mark Goadrich
#
# Cells is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cells is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cells.  If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import math
import pygame
from random import randint, shuffle
from pieces import EscapeArea, Cell, Hideout
from sprites import Text, Group, Guard
from colors import blue, yellow, black, white
import cursor

from gettext import gettext as _

################################################################################
# Game
################################################################################

class Game():

    def __init__(self, fps = 30):
        self.fps = fps

    def load_all(self):
        pygame.init()
        self.cursor = pygame.cursors.compile(cursor.cursor_data)
        pygame.mouse.set_cursor((32,32), (1,1), *self.cursor)
        info = pygame.display.Info()
        self.ScreenWidth = info.current_w
        self.ScreenHeight = info.current_h
        self.screen = pygame.display.get_surface()
        if not(self.screen):
            self.screen = pygame.display.set_mode((self.ScreenWidth, 
                                        self.ScreenHeight), pygame.FULLSCREEN)

        # time stuff
        self.clock = pygame.time.Clock()
             
        # how many cells
        self.cell_count = 2

        # let's keep score
        self.move_count = 0

    def dist(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def polToCart(self, r, angle):
        # here the center is (512, 384)
        angle *= math.pi / 180.0
        x = int(r * math.cos(angle)) + 600
        y = int(r * math.sin(angle)) + 450
        return x, y
        
    def drawBoard(self):
        # this is the giant colorful thing you see when you start the game
        pos = (600, 450)
        pygame.draw.circle(self.background, black, pos, 354)
        pygame.draw.circle(self.background, (0,255,255), pos, 350)
        pygame.draw.circle(self.background, black, pos, 254)
        pygame.draw.circle(self.background, blue, pos, 250)
        pygame.draw.circle(self.background, black, pos, 89)
        pygame.draw.circle(self.background, yellow, pos, 85)

    def setupBoard(self):
        # make board
        self.background = pygame.Surface(self.screen.get_size()).convert()
        r, g, b = randint(50, 255), 0, randint(50, 150)
        self.background.fill((r,g,b))
        self.drawBoard()

        # make pieces
        self.escArea = EscapeArea(self)
        
        # a list that corresponds to a hiding space's allignment
        # weather a hiding space is hostile or friendly
        hf = ["h", "f"] * (self.cell_count // 2) # <- this gives us an int
        if self.cell_count % 2 == 1:
            hf += ["f"]
        shuffle(hf)
            
        # a list that keeps track of cells
        self.cells = []

        # put the cells in the list
        for i in range(0, self.cell_count):
            x = Cell(self, i)
            self.cells.append(x)
        
        # create a list of numbers [1 : the number of cells)
        # this is closed on the left
        nums = list(range(1, self.cell_count))
        shuffle(nums)

        n = 0
        while len(nums) != 0:
            x = nums.pop(0)
            y = Hideout(self, x, self.cells[x], hf.pop())
            self.cells[n].setAdjHS(y)
            self.cells[x].setMyHS(y)
            n = x

        y = Hideout(self, 0, self.cells[0], hf.pop())
        self.cells[n].setAdjHS(y)
        self.cells[0].setMyHS(y)
       
        # now shuffle the cells (and effectively the hiding spaces)
        # this game is not solvable if the number of cells mod 4
        # is 0 or 1 and the corresponding hiding space
        # for each cell is the hiding space to the right of it
        # so we shuffle extra if it happens ;)
        solvable = False
        while not solvable:
            if self.cell_count % 4 == (2 or 3):
                solvable == True
                break             
            count = 0
            shuffle(self.cells)
            for i in range(0, self.cell_count):
                a = self.cells[i].species 
                b = self.cells[(i + 1) % self.cell_count].adj_hs.species
                if a == b:
                    count += 1
                else:
                    solvable == True
                    break
            if count != self.cell_count:
                solvable = True

        # and let the cells and hiding spaces know where they've been put
        for j in range(0, self.cell_count):
            a = self.cells[j]
            a.seti(j)
            a.getAdjHS().seti(j)
            angle = (((360.0 / self.cell_count) * j) - 90) % 360
            x1, y1 = self.polToCart(245, angle)
            x2, y2 = self.polToCart(140, angle)
            a.setPos(x1, y1)
            a.getAdjHS().setPos(x2, y2)

        # lastly... sprites
        self.guard = Guard(self)
        self.guards = Group((self.guard))
        for i in self.cells:
            i.makePrisoners()

    def resetGame(self):
         already_reset = True
         for cell in self.cells:
             if len(cell.prisoners) != 2:
                 already_reset = False
         if not already_reset:
             self.move_count += 1
             for cell in self.cells:
                 cell.reset()
       
    def gameloop(self):
        self.setupBoard()
        playing = True
        while playing:
            self.clock.tick(self.fps)

            text1 = Text(str(self.move_count), 
                        size = int(35), 
                        color = black)
            text1.rect.center = (600, 450)
            text2 = Text(_("(h)elp"), size = 50)
            text2.rect.topleft = (10, 10)
            self.text = Group((text1, text2))

            if (len(self.escArea.prisoners.sprites()) == self.cell_count
                and self.guard.moving == False):
                pygame.time.wait(3000)
                playing = False

            while Gtk.events_pending():
                Gtk.main_iteration()

            # Handle Input Events
            for event in pygame.event.get():
                # this one is for the box in the top right marked X
                if event.type == pygame.QUIT:
                    playing, self.running = False, False
                # and this one is for the "ESC" key
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.move_count = 0
                        playing = False
                        self.makeMenu()
                        self.cell_count = 1
                    if event.key == pygame.K_r:
                        self.resetGame()
                    elif event.key == pygame.K_h:
                        self.help()
       
            # update sprites
            self.guards.update()
            self.escArea.prisoners.update()
            for i in range(0,self.cell_count):
                self.cells[i].prisoners.update()
                self.cells[i].getAdjHS().prisoners.update()
                self.cells[i].text.update()
                
            # draw everything
            self.screen.blit(self.background, (0, 0))
            self.escArea.prisoners.draw(self.screen)
            for i in range(0,self.cell_count):
                a = self.cells[i]
                a.text.draw(self.screen)
                a.getAdjHS().text.draw(self.screen)
                a.prisoners.draw(self.screen)
                a.getAdjHS().prisoners.draw(self.screen)
            self.guards.draw(self.screen)
            self.text.draw(self.screen)

            # finally, refresh the screen
            pygame.display.flip()
    
    def makeMenu(self):
        self.new_game = False
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(yellow)
        cell_text = Text(_("Cells"), size = int(160))
        cell_text.rect.center = ((600,450))
        self.text = Group((cell_text))

        prompt_text = Text(_("press any key to begin"), size = int(35))
        prompt_text.rect.center = (600,530)
        self.flashing_text = Group((prompt_text))       

    def help(self):
        t = 40
        a = Text(_("Try and get 1 of species in the yellow escape area."), 
                 size = t)
        b = Text(_("Click a cell to send the guard there."), 
                 size = t)
        b.rect.top = a.rect.bottom + 1
        c = Text(_("Prisoners can escape iff the adjacent hiding space is"),
                 size = t)
        c.rect.top = b.rect.bottom + 1
        d = Text('    ' + _("red and empty or green and occupied."), 
                 size = t)
        d.rect.top = c.rect.bottom + 1
        e = Text(_("Hit 'Esc' to return to the menu."), 
                 size = t)
        e.rect.top = d.rect.bottom + 1
        f = Text(_("Press 'r' to reset the current game"), 
                 size = t)
        f.rect.top = e.rect.bottom + 1
        text = Group((a, b, c, d, e, f))

        helping = True
        while helping:
            self.screen.fill(white)   
            text.draw(self.screen)

            while Gtk.events_pending():
                Gtk.main_iteration()

            for event in pygame.event.get():
                # this one is for the box in the top right marked X
                if event.type == pygame.QUIT:
                    self.running = False
                # and this one is for the "ESC" key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        helping = False

            pygame.display.flip()
     
    def mainloop(self):
        self.load_all()
        self.makeMenu()
        self.running = True
        count = 0
        while self.running:
            self.clock.tick(self.fps)

            self.screen.blit(self.background, (0, 0))

            while Gtk.events_pending():
                Gtk.main_iteration()

            for event in pygame.event.get():
                # this one is for the box in the top right marked X
                if event.type == pygame.QUIT:
                    self.running = False
                # and this one is for the "ESC" key
                if event.type == pygame.KEYDOWN:
                    if self.cell_count == 2 and not self.new_game:
                        self.new_game = True

            if self.new_game == True:
                if self.cell_count == 9:
                    self.new_game = False
                self.gameloop()
                self.cell_count += 1
                
            if self.cell_count == 9:
                self.background.fill(black)
                text1 = Text(_("Congratulations"), color = white, size = 120)
                text2 = Text(_("You finished in %s moves.") % str(self.move_count),
                             color = white, size = 60)
                text2.rect.top = text1.rect.bottom + 10
                self.text = Group((text1, text2))
            
            self.text.draw(self.background)
            
           
            if self.cell_count == 2:
                count += 1
                if (count / (self.fps / 2)) % 2 == 1:
                    self.flashing_text.draw(self.screen)
                    
            pygame.display.flip()

def main():
    cells = Game()
    cells.mainloop()

if __name__ == "__main__":
    main()

