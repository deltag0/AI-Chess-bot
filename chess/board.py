import pygame
from constants import *

class Game():
    def __init__(self) -> None:
        pass

    def showBoard(self, surface):
        lastIdx = 1
        for row in range(ROWS):
            for col in range(COLS):
                if (row % 2 == 0):
                    if (lastIdx % 2 == 0):
                        color = (118, 150, 86)
                    else:
                        color = (238, 238, 210)
                else:
                    if (lastIdx % 2 == 1):
                        color = (118, 150, 86)
                    else:
                        color = (238, 238, 210)
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)
                lastIdx += 1
