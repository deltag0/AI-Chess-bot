import chess as ch  # chess library used for the board, moves, captures, etc.
import chess.svg
import chess
import chess.svg
import pygame
import sys
import time
from constants import *
from board import Game, findLegalMoves
from objects import *
from controls import Dragger
from engine import Engine
from collections import defaultdict

def fenConverter(string: str) -> dict[str: str]:
    """
    fenConverter converts the string string from fen notation (https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation)
    into a dictionary whose keys are squares on the chess board such as a8, a7, c3, etc. Uppercase letters denote white pieces 
    while lowercase letters denote black pieces. A 0 means the square is empty. Function will be called every time the board is 
    updated to see if any visual changes need to be made.
    """
    boardRows = string.split("/")
    piecePositions = {}
    prevNum = 0
    for row in range(len(boardRows)):
        for col in range(len(boardRows[row])):
            # if element is a digit, add corresponding amount of empty squares ot the board, otherwise add the piece
            if (boardRows[row][col].isdigit()):
                for i in range(int(boardRows[row][col])):
                    piecePositions[chr(ord('a') + prevNum + i) + str(8 - row)] = '0'
                prevNum += int(boardRows[row][col])
                continue
            else:
                piecePositions[chr(ord('a') + prevNum) + str(8 - row)] = boardRows[row][col]
                prevNum += 1
        prevNum = 0
    return piecePositions

def findLenUntilSpace(object: str, start: int) -> int:
    end = start
    for i in range(start, len(object)):
        if object[i] != ' ':
            end = i
        else:
            break
    return end

def hasPiece(board: dict[str: str], pos: str) -> bool:
    """
        Returns true if the position has a piece, false otherwise 
    """
    if (board[pos] != '0'):
        return True
    else:
        return False


class MainWindow():
    """
    The MainWindow is the program that will create the chessboard.
    """
    def __init__(self, board: chess.Board):
        self.board = board
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.whitePieces = 16
        self.blackPieces = 16
        self.sanStack = []
        self.transpositions = defaultdict(lambda: [None, None])
        pygame.display.set_caption("Chess")

    def startGame(self):
        """
        startGame method is the loop that runs the chess game
        """
        board = self.board
        dragging = False
        draggedPiece = None
        mouseX = 0
        mouseY = 0
        moveCount = 0
        initialRow = 0
        initialCol = 0
        openingEnd = False
        # main game loop
        while (self.board.is_checkmate() == False and self.board.is_stalemate() == False
               and self.board.is_fivefold_repetition() == False):
            self.currBoard = fenConverter(self.board.board_fen())
            self.game = Game(self.currBoard, self.board, dragging, draggedPiece, mouseX, mouseY, initialRow, initialCol)
            self.engine = Engine(self.currBoard, self.board, self.whitePieces, self.blackPieces, self.transpositions)
            dragger = self.game.dragger
            game = self.game
            game.showBoard(self.screen)
            game.show_pieces(self.screen)
            # if we drag a piece, show that we drag it
            if (dragger.dragging):
                dragger.updateBlit(self.screen)
            for event in pygame.event.get():

                # event for exiting game
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    sys.exit()

                if (board.turn):
                    # event for clicking piece
                    if (event.type == pygame.MOUSEBUTTONDOWN):
                        mouseX, mouseY = event.pos
                        dragger.mouseX = mouseX
                        dragger.mouseY = mouseY
                        clickedRow = str(8 - (dragger.mouseY // SQSIZE))
                        clickedCol = chr(dragger.mouseX // SQSIZE + ord('a'))
                        pos = clickedCol + clickedRow

                        # event for a square with a piece
                        if (hasPiece(self.currBoard, pos)):
                            name = self.currBoard[pos]
                            # if the piece name is lowercase, it's black
                            if (name.islower()):
                                color = 'black'
                            else:
                                color = 'white'
                            draggedPiece = Piece(name, color, 0, findLegalMoves(self.board.legal_moves, pos))
                            dragger.piece = draggedPiece
                            initialRow = clickedRow
                            initialCol = clickedCol
                            dragger.initialRow = clickedRow
                            dragger.initialCol = initialCol
                            dragging = True
                            dragger.dragging = dragging
                    # event for moving piece
                    elif (event.type == pygame.MOUSEMOTION):
                        # event if piece is getting dragged
                        if (dragger.dragging == True):
                            mouseX, mouseY = event.pos
                            dragger.mouseX = mouseX
                            dragger.mouseY = mouseY
                            game.showBoard(self.screen)
                            game.show_pieces(self.screen)
                            dragger.updateBlit(self.screen)

                    # event for placing (releasing) piece
                    elif (event.type == pygame.MOUSEBUTTONUP):
                        mouseX, mouseY = event.pos
                        currRow = str(8 - (mouseY // SQSIZE))
                        currCol = chr(mouseX // SQSIZE + ord('a'))
                        square = currCol + currRow
                        if (currRow == '8' and self.currBoard[dragger.initialCol + dragger.initialRow] == 'P'):
                            square += 'q'
                        print(dragger.initialCol + dragger.initialRow)
                        # if there's a piece on the square and the move made is valid, update the position
                        if (dragger.piece != None and square in dragger.piece.moves):
                            moveCount += 1
                            if (self.currBoard[square[:2]] != '0'):
                                self.blackPieces -= 1
                            self.sanStack.append(self.board.san(ch.Move.from_uci(dragger.initialCol + dragger.initialRow + square)))
                            self.board.push(ch.Move.from_uci(dragger.initialCol + dragger.initialRow + square))
                        game.showBoard(self.screen)
                        game.show_pieces(self.screen)


                        dragging = False
                        dragger.dragging = dragging
                        draggedPiece = None
                        dragger.piece = draggedPiece
                else:
                    stop = False
                    if openingEnd == False:
                        currPos = " ".join(self.sanStack)
                        posLen = len(currPos)
                        game.showBoard(self.screen)
                        game.show_pieces(self.screen)
                        with open('games.txt', 'r') as f:
                            i = 0
                            for line in f:
                                print(i)
                                i += 1
                                if (currPos == line[:posLen]):
                                    end = findLenUntilSpace(line, posLen + 1)
                                    if end == posLen + 1:
                                        continue
                                    self.sanStack.append(line[posLen + 1:end + 1])
                                    move = self.board.parse_san(line[posLen + 1:end + 1])
                                    if self.currBoard[move.uci()[2:]] != '0':
                                        self.whitePieces -= 1
                                    self.board.push(move)
                                    self.currBoard = fenConverter(self.board.board_fen())
                                    game.showBoard(self.screen)
                                    game.show_pieces(self.screen)
                                    print(self.sanStack)
                                    stop = True
                                    break
                            if stop:
                                continue
                            openingEnd = True
                    else:
                        start_time = time.time()
                        print(self.engine.search(DEPTH, False, float("-inf"), float("inf")))
                        print(time.time() - start_time)
                        if (self.currBoard[self.engine.move.uci()[2:]] != '0'):
                            self.whitePieces -= 1
                        self.transpositions = self.engine.transpositions
                        self.sanStack.append(self.board.san(self.engine.move))
                        self.board.push(self.engine.move)
                        print("done: ", self.engine.materialValue)
                        self.currBoard = fenConverter(self.board.board_fen())
                        game.showBoard(self.screen)
                        game.show_pieces(self.screen)

            pygame.display.update()
        print(board.outcome().winner)


newBoard = ch.Board()
# newBoard.set_board_fen("8/3K4/4P3/8/8/8/6k1/7q")
window = MainWindow(newBoard)
window.startGame()
