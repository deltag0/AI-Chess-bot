import chess as ch  # chess library used for the board, moves, captures, etc.
import chess.svg
import chess
import chess.svg
import pygame
import sys
from constants import *
from board import Game, findLegalMoves
from objects import *
from controls import Dragger
from engine import Engine

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

def hasPiece(board: dict[str: str], pos: str) -> bool:
    """
        Returns true if the position has a piece, false otherwise 
    """
    if (board[pos] != '0'):
        return True
    else:
        return False


class Main():
    def __init__(self, board):
        """
        The board is going to be the visual chess board that will be seen
        by users.
        """
        self.board = board

    def startGame(self):
        color = None
        while (color != "b" and color != "w"):
            color = input("Play as white (\"w\") or black (\"b\"): ")
        if (color == "b"):
            while (self.board.is_checkmate() == False):
                self.playHumanMove()
                print(self.board)
            print(self.board)
            print(self.board.outcome())

        elif (color == "w"):
            while (self.board.is_checkmate() == False):
                self.playHumanMove()
                print(self.board)
            print(self.board)
            print(self.board.outcome())

    def playHumanMove(self):
        try:
            print(self.board.legal_moves)
            print("To undo your last move, type \"undo\".")
            play = input("Your move: ")
            if (play == "undo"):
                self.board.pop()
                self.board.pop()
                self.playHumanMove()
                return
            self.board.push_san(play)
        except:
            self.playHumanMove()

    def showBoard(maxDepth = 150):
        board = ch.board()

        for _ in range(depth):
            all_moves = list(board.legal_moves)

    def engine(self, candidate, depth):
        if (depth == self.maxDepth or self.board.legal_moves.count() == 0):
            return self.evalFunct()


class MainWindow():
    """
    The MainWindow is the program that will create the chessboard.
    """
    def __init__(self, board: chess.Board):
        self.board = board
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
        # main game loop
        while (self.board.is_checkmate() == False and self.board.is_stalemate() == False
               and self.board.is_fivefold_repetition() == False):
            self.currBoard = fenConverter(self.board.board_fen())
            self.game = Game(self.currBoard, self.board, dragging, draggedPiece, mouseX, mouseY, initialRow, initialCol)
            self.engine = Engine(self.currBoard, self.board)
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
                        print(dragger.initialCol + dragger.initialRow)
                        # if there's a piece on the square and the move made is valid, update the position
                        if (dragger.piece != None and square in dragger.piece.moves):
                            moveCount += 1
                            self.board.push(ch.Move.from_uci(dragger.initialCol + dragger.initialRow + square))
                        game.showBoard(self.screen)
                        game.show_pieces(self.screen)


                        dragging = False
                        dragger.dragging = dragging
                        draggedPiece = None
                        dragger.piece = draggedPiece
                else:
                    if (moveCount > 10):
                        game.showBoard(self.screen)
                        game.show_pieces(self.screen)
                        # self.currBoard = fenConverter(self.board.board_fen())
                        print(self.engine.search(DEPTH, False, float("-inf"), float("inf")))
                        self.board.push(self.engine.move)
                        print("done: ", self.engine.materialValue)
                    if (moveCount == 1):
                        self.board.push(ch.Move.from_uci("e7e5"))
                    elif (moveCount == 3):
                        self.board.push(ch.Move.from_uci("b8c6"))
                    elif (moveCount == 5):
                        self.board.push(ch.Move.from_uci("h7h6"))
                    elif (moveCount == 7):
                        self.board.push(ch.Move.from_uci("f7f5"))
                    elif (moveCount == 9):
                        self.board.push(ch.Move.from_uci("d7d5"))
                    self.currBoard = fenConverter(self.board.board_fen())
                    game.showBoard(self.screen)
                    game.show_pieces(self.screen)
                    moveCount += 1
            pygame.display.update()
        print(board.outcome().winner)


newBoard = ch.Board()
window = MainWindow(newBoard)
window.startGame()
