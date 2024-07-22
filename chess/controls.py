import pygame
from constants import *

class Dragger:
    def __init__(self, dragging, piece, mouseX, mouseY, initialRow, initialCol):
        self.piece = piece
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.initialRow = initialRow
        self.initialCol = initialCol
        self.dragging = dragging
        self.piece = piece

    def updateBlit(self, surface):
        self.piece.set_texture(size=128)
        texture = self.piece.texture
        img = pygame.image.load(texture)
        img_center = (self.mouseX, self.mouseY)
        self.piece.texture_rect = img.get_rect(center=img_center)
        surface.blit(img, self.piece.texture_rect)
