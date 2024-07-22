import pygame
from constants import *
import chess as ch  # chess library used for the board, moves, captures, etc.
import chess
import pygame
from objects import *
from controls import Dragger

def findLegalMoves(allMoves: list[chess.Move], currPos: str) -> set[str]:
    """
    Finds all legal moves of the piece at currPos which is a string representing 
    a square on the board, such as a8 using allMoves which is a list containing 
    every legal move of every piece
    """
    legalMoves = set()
    for location in allMoves:
        pos = str(location)[2:]
        try:
            # add move if it's legal
            if (chess.Move.from_uci(currPos + pos) in allMoves):
                legalMoves.add(pos)
        except ch.InvalidMoveError:
            pass
    return legalMoves


class Game():
    """
    Class to help display images to player
    """
    def __init__(self, currBoard, board, dragging, draggedPiece, mouseX, mouseY, initialRow, initialCol) -> None:
        self.board = board
        self.currBoard = currBoard
        self.dragger = Dragger(dragging, draggedPiece, mouseX, mouseY, initialRow, initialCol)
        self.dragging = dragging
        self.initialRow = initialRow
        self.initialCol = initialCol

    def showBoard(self, surface):
        """
       The showBoard method displays the 8x8 chess board with green and white tiles. The default setting
       faces white towards the human player.
        """
        lastIdx = 1
        for row in range(ROWS):
            for col in range(COLS):
                # choose color of square
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

    def show_pieces(self, surface):
        """
        show_pieces shows all pieces that are on the board.
        """
        currBoard = self.currBoard
        for pos in list(currBoard.keys()):
            # if there's no piece on the square, do nothing, otherwise, load it in
            if (currBoard[pos] == '0' or (self.dragging == True and pos == (self.initialCol + self.initialRow))):
                pass
            else:
                col, row = (ord(pos[0]) - ord('a'), 8 - int(pos[1]))
                if (currBoard[pos].islower()):
                    color = "black"
                else:
                    color = "white"
                moves = findLegalMoves(self.board.legal_moves, pos)
                piece = Piece(currBoard[pos], color, 0, moves)
                img = pygame.image.load(piece.texture)
                img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                piece.texture_rect = img.get_rect(center=img_center)
                surface.blit(img, piece.texture_rect)