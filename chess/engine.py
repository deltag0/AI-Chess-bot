from objects import Piece
from board import findLegalMoves
import chess as ch
from constants import *
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
            # if element is a digit, add corresponding amount of empty squares on the board, otherwise add the piece
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

def findColor(name: str) -> str:
    if (name.islower()):
        return "black"
    else:
        return "white"


class Engine():
    """
    Class that controles the engine with the moves
    """
    def __init__(self, board: dict[str: str], pythonBoard: ch.Board) -> None:
        self.board = board
        self.pythonBoard = pythonBoard
        self.materialValue = 0
        self.move = None

    def orderMoves(self, moves: set[str], start: str) -> list[str]:
        valList = []
        moveName = self.board[start]
        moveColor = findColor(moveName)
        movePiece = Piece(moveName, moveColor, 0, set())
        for move in moves:
            targetName = self.board[move]
            if (targetName != '0'):
                targetColor = findColor(targetName)
                targetPiece = Piece(targetName, targetColor, 0, set())
                val = abs(targetPiece.value)
                val = 10 * val - abs(movePiece.value)
            else:
                val = 0
            valList.append(val)
        moves = list(moves)
        combined = list(zip(moves, valList))
        return [move[0] for move in sorted(combined, key=lambda x: x[1], reverse=True)]



    def evaluate(self, isWhite: bool):
        materialValue = 0
        squares = list(self.board.keys())
        if (self.pythonBoard.is_stalemate()):
            return 0
        if (self.pythonBoard.is_checkmate() and self.move != None):
            if (isWhite):
                return float('-inf')
            else:
                return float('inf')
        for square in squares:
            if (self.board[square] != '0'):
                name = self.board[square]
                if (name.islower()):
                    color = "black"
                else:
                    color = "white"
                moves = findLegalMoves(self.pythonBoard.legal_moves, square)
                piece = Piece(name, color, 0, moves)
                materialValue += piece.value
        return materialValue

    def search(self, depth: int, whiteTurn: bool, alpha: int, beta: int):
        possibleMoves = {}
        end = False
        squares = list(self.board.keys())
        if (depth == 0):
            return self.evaluate(whiteTurn)
        # trying to maximize the score
        if (whiteTurn):
            for square in squares:
                if (self.board[square] != '0' and self.board[square].isupper()):
                    possibleMoves[square] = self.orderMoves(findLegalMoves(self.pythonBoard.legal_moves, square), square)
            bestEvaluation = float('-inf')
            whiteSquares = list(possibleMoves.keys())
            # go through all possible moves of each white piece
            for whiteSquare in whiteSquares:
                for move in possibleMoves[whiteSquare]:
                    self.pythonBoard.push(ch.Move.from_uci(whiteSquare + move))
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    evaluation = self.search(depth - 1, not whiteTurn, alpha, beta) # alpha best for white, beta best for black
                    if (evaluation > bestEvaluation):
                        bestEvaluation = evaluation
                    self.pythonBoard.pop()
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    alpha = max(alpha, evaluation)
                    if (beta <= alpha):
                        end = True
                        break
                if (end):
                    break
            return bestEvaluation
        # trying to minimize the score
        else:
            for square in squares:
                if (self.board[square] != '0' and self.board[square].islower()):
                    possibleMoves[square] = self.orderMoves(findLegalMoves(self.pythonBoard.legal_moves, square), square)
            print(possibleMoves)
            bestEvaluation = float('inf')
            blackSquares = list(possibleMoves.keys())
            # go through all possible moves of each black piece
            for blackSquare in blackSquares:
                for move in possibleMoves[blackSquare]:
                    self.pythonBoard.push(ch.Move.from_uci(blackSquare + move))
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    evaluation = self.search(depth - 1, not whiteTurn, alpha, beta)
                    if (evaluation < bestEvaluation):
                        bestEvaluation = evaluation
                        if (depth == DEPTH):
                            self.move = ch.Move.from_uci(blackSquare + move)
                            self.materialValue = bestEvaluation
                    self.pythonBoard.pop()
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    beta = min(beta, evaluation)
                    if (beta <= alpha):
                        end = True
                        break
                if (end):
                    break
            return bestEvaluation
