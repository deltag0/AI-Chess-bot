import chess as ch  # chess library used for the board, moves, captures, etc.
import chess.svg
import chess
import chess.svg
import pygame
import sys
from constants import *
from board import Game
from objects import *

def fenConverter(string: str) -> dict[str: str]:
    boardRows = string.split("/")
    piecePositions = {}
    prevNum = 0
    for row in range(len(boardRows)):
        for col in range(len(boardRows[row])):
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


def findLegalMoves(allMoves: list[chess.Move], currPos: str) -> set[str]:
    legalMoves = set()
    for location in allMoves:
        pos = str(location)[2:]
        if (chess.Move.from_uci(currPos + pos) in allMoves):
            legalMoves.add(pos)
    return legalMoves



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
    def __init__(self, board: chess.Board):
        self.board = board
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")

    def startGame(self):
        self.game = Game()
        game = self.game
        while (self.board.is_checkmate() == False):
            self.currBoard = fenConverter(self.board.board_fen())
            game.showBoard(self.screen)
            self.show_pieces(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def show_pieces(self, surface):
        currBoard = self.currBoard
        for pos in list(currBoard.keys()):
            if (currBoard[pos] == '0'):
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

newBoard = ch.Board()
window = MainWindow(newBoard)
window.startGame()
# game = Main(newBoard)
# game.startGame()
