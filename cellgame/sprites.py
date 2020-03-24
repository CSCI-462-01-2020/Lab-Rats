#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# sprites.py is part of Cells. Cells is free software: you can 
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

import math
import pygame
from colors import red, yellow, black, grey, white
from random import randint

################################################################################
# the Super Group... because regular groups aren't good enough
################################################################################

class Group(pygame.sprite.Group):
    # We'll call it a quick fix; I meant to add more.
    def set_pos(self, x, y): self.x, self.y = x, y
    
################################################################################
# Text Sprite
################################################################################

class Text(pygame.sprite.Sprite):
    def __init__(self, text, size, color = black):
        pygame.sprite.Sprite.__init__(self)
        default = pygame.font.get_default_font()
        font = pygame.font.Font(default, size)
        self.original = font.render(text, True, color)
        self.image = self.original.copy()
        self.rect = self.image.get_rect()

################################################################################
# Moving Sprites are the way to go
################################################################################

class MovingSprite(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game

    def angle(self, x, y):
        distance = self.game.dist(self.rect.centerx, self.rect.centery, x, y)
        angle = math.acos(float(x - self.rect.centerx) / float(distance))
        angle *= 180.0 / math.pi # because pygame likes degrees
        if y > self.rect.centery:
            angle = 360 - angle
        return angle

    def move(self, angle):
        dx = math.cos(angle * math.pi / 180) * self.speed
        dy = -math.sin(angle * math.pi / 180) * self.speed
        self.rect.move_ip(dx, dy)


################################################################################
# The Prisoner
################################################################################

class Prisoner(MovingSprite):
    def __init__(self, game, species, x, y, LorR):
        MovingSprite.__init__(self, game)
        self.species = species
        self.speed = randint(16, 22)
        self.LorR = LorR

        # this is the image you see most of the time
        self.original = pygame.Surface((40,40)).convert()
        self.original.fill(yellow)
        pygame.draw.circle(self.original, black, (20,20), 20)
        self.original.set_colorkey(yellow)
        self.rect = self.original.get_rect()

        # this is the one you see when the mouse is hovering
        # over it and it's in the escape area
        self.selected_img = self.original.copy()
        pygame.draw.circle(self.selected_img, grey,(20,20), 17)

        # let the original image be the one we start off with
        self.image = self.original.copy()

        # let's also let everyone know what kind of animal we are
        text = Text(str(self.species + 1), size = int(20), color = white)
        text.rect.center = self.rect.center
        self.text = Group((text))
        self.text.draw(self.image)
        
        if self.LorR == 'left':
            self.rect.center = (x - 21, y)
        else:
            self.rect.center = (x + 21, y)
    
    def update(self):
        m = pygame.mouse.get_pos()
        d = self.game.dist(m[0], m[1], self.rect.centerx, self.rect.centery)
        button1, button2, button3 = pygame.mouse.get_pressed()
        a = self.game.escArea.prisoners
        if (d <= 20 and
            self in a.sprites() and 
            not self.game.guard.moving):
            self.image = self.selected_img.copy()
            self.text.draw(self.image)
            if (button1 or button2 or button3):
                self.game.move_count += 1
                a.remove(self)
                for i in range(0, self.game.cell_count):
                    if self.species == self.game.cells[i].getMyHS().species:
                        self.game.cells[i].getMyHS().addPrisoner(self)
        else:
            self.image = self.original.copy()
            self.text.draw(self.image)
   
        x = self.groups()[0].x
        y = self.groups()[0].y

        if self.LorR == 'left': x -= 21
        else: x += 21

        d = self.game.dist(x, y, 600, 450)
        if d < 85:
            angle = (((360.0 / self.game.cell_count) * self.species) - 90) % 360
            x, y = self.game.polToCart(int(60), angle)

        d = self.game.dist(x, y, self.rect.centerx, self.rect.centery)
        if d > self.speed: self.move(self.angle(x, y))
        else: self.rect.center = (x, y)
         

################################################################################
# The Guard
################################################################################
           
class Guard(MovingSprite):
    def __init__(self, game):
        MovingSprite.__init__(self, game)
        
        self.speed = 15
        self.image = pygame.Surface((40,40))
        self.image.fill(white)
        pygame.draw.circle(self.image, black, (20,20), 20)
        pygame.draw.circle(self.image, red, (20,20), 17)
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.moving = False
        self.rect.center = (-100, -100)
        self.destx, self.desty = 50, 50
        self.i ,self.stop = 0, 0

    def setDest(self, dest):
        self.destx, self.desty = dest[0], dest[1]
        
    def circ(self, x, y):
        distance = self.game.dist(600, 450, x, y)
        angle = math.acos(float(x - 600) / float(distance))
        angle *= 180.0 / math.pi # because pygame likes degrees
        if y > 450:
            angle = 360 - angle
        angle = (480 - angle) % 360
        i = int(angle / (360.0 / self.game.cell_count))
        return i

    def path(self, i):
        d = int(350)
        angle = []
        for j in range(-90, 400, (360 // self.game.cell_count)):
            angle.append(j)
        x = (int(d * math.cos(angle[i] * math.pi / 180.0)) + 600)
        y = (int(d * math.sin(angle[i] * math.pi / 180.0)) + 450)
        return (x,y)
   
    def update(self):
        button1, button2, button3 = pygame.mouse.get_pressed()
        if not self.moving:
            for i in range(0, len(self.game.cells)):
                x, y = self.game.cells[i].x, self.game.cells[i].y
                if self.game.cells[i].isSelected():
                    pygame.draw.circle(self.game.background, grey, (x, y), 50)

                    if (button1 or button2 or button3):
                        self.game.move_count += 1
                        self.moving = True
                        self.i = i
                        self.stop = self.i
                        self.setDest(self.path(self.i))
                else:
                    pygame.draw.circle(self.game.background, white, (x, y), 50)

         
        d = self.game.dist(self.rect.centerx, self.rect.centery,
                           self.destx, self.desty)

        if d > self.speed and self.moving:
            self.move(self.angle(self.destx, self.desty))

        elif self.moving:
            self.game.cells[self.i].update()
            self.game.cells[self.i].getAdjHS().vacate()
            self.i = (self.i + 1) % self.game.cell_count
            if self.i != self.stop:
                self.setDest(self.path(self.i))
            else: self.moving = False


