from objects import Piece
from board import findLegalMoves
import chess as ch
from constants import *
from collections import defaultdict

def fenConverter(string: str) -> dict[str: str]:
    """
    fenConverter converts the string string from fen notation (https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation)
    into a dictionary whose keys are squares on the chess board such as a8, a7, c3, etc. Uppercase letters denote white pieces 
    while lowercase letters denote black pieces. A 0 means the square is empty. Function will be called every time the board is 
    updated.
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
    """
    finColor finds the color of the piece with the name name.
    The name of the piece is how it's used in fen Notation, so 
    p (black pawn), P (white pawn), n (white knight), etc.
    """
    if (name.islower()):
        return "black"
    else:
        return "white"


class Engine():
    """
    Class that controls the engine with the moves
    """
    def __init__(self, board: dict[str: str], pythonBoard: ch.Board, whitePieces: int, blackPieces: int, transpositions: defaultdict) -> None:
        self.board = board
        self.pythonBoard = pythonBoard
        self.materialValue = 0
        self.move = None
        self.transpositions = transpositions
        self.whitePieces = whitePieces
        self.blackPieces = blackPieces

    def updateBoard(self, originalPos: str, newPos: str) -> None:
        piece = self.board[originalPos]
        self.board[originalPos] = '0'
        self.board[newPos] = piece

    def attackedByPawn(self, start: str, color: str) -> bool:
        """
        attackedByPawn detects if a piece at position start with the color color is attacked by a pawn.
        A pinned pawn will count as an attacker.
        """
        if (color == "white"):
            left = ""
            right = ""
            # check row
            if (start[1] != '8'):
                # check column
                if (start[0] != 'a'):
                    left = chr(ord(start[0]) - 1) + str(int(start[1]) + 1)
                    if (self.board[left] == 'p' and self.pythonBoard.is_pinned(ch.BLACK, ch.parse_square(left)) == False):
                        return True
                if (start[0] != 'h'):
                    right = chr(ord(start[0]) + 1) + str(int(start[1]) + 1)
                    if (self.board[right] == 'p' and self.pythonBoard.is_pinned(ch.BLACK, ch.parse_square(right)) == False):
                        return True
                return False
        else:
            left = ""
            right = ""
            # check row
            if (start[1] != '1'):
                # check column
                if (start[0] != 'a'):
                    right = chr(ord(start[0]) - 1) + str(int(start[1]) - 1)
                    if (self.board[right] == 'P' and self.pythonBoard.is_pinned(ch.WHITE, ch.parse_square(right)) == False):
                        return True
                if (start[0] != 'h'):
                    left = chr(ord(start[0]) + 1) + str(int(start[1]) - 1)
                    if (self.board[left] == 'P' and self.pythonBoard.is_pinned(ch.WHITE, ch.parse_square(left)) == False):
                        return True
                return False

    def orderMoves(self, moves: set[str], start: str) -> list[str]:
        """
        orderMoves sorts the moves in an order with estimates to how good the
        move is. There are 3 criterias: 
        Move to capture a piece, 
        Move to promote,
        Move that gets a piece attacked by a pawn
        Checkmate
        """
        valList = []
        moveName = self.board[start]
        moveColor = findColor(moveName)
        movePiece = Piece(moveName, moveColor, 0, set())
        for move in moves:
            move = move[:2]
            targetName = self.board[move]
            # if there's a piece on the square, check the captured piece
            if (targetName != '0'):
                targetColor = findColor(targetName)
                targetPiece = Piece(targetName, targetColor, 0, set())
                val = abs(targetPiece.value)
                val = 10 * val - abs(movePiece.value)
            else:
                val = 0
            self.pythonBoard.push(ch.Move.from_uci(start + move))
            if (self.pythonBoard.is_checkmate):
                val += 10000000
            self.pythonBoard.pop()
            # check for promotion
            if ((move[1] == '8' and moveName == 'P') or (move[1] == '1' or moveName == 'p')):
                val += 9
            # check for pawn attacks
            if (self.attackedByPawn(move, moveColor)):
                val -= movePiece.value
            valList.append(val)
        moves = list(moves)
        combined = list(zip(moves, valList))
        return [move[0] for move in sorted(combined, key=lambda x: x[1], reverse=True)]

    def endGameEval(self, endgameWeight: float, isWhite: bool) -> int:
        """
        endGameEval gives a higher score to moves that force the white 
        king to the backRanks when the game is closer to the end (when
        white has less pieces).
        """
        eval = 0
        blackKingSquare = ch.square_name(self.pythonBoard.king(ch.BLACK))
        blackKingRank = int(blackKingSquare[1])
        blackKingFile = ord(blackKingSquare[0]) - ord('a') + 1

        whiteKingSquare = ch.square_name(self.pythonBoard.king(ch.WHITE))
        whiteKingRank = int(whiteKingSquare[1])
        whiteKingFile = ord(whiteKingSquare[0]) - ord('a') + 1
        if (isWhite == False):
            EnemyDistToCentreFile = max(3 - whiteKingFile, whiteKingFile - 4)
            EnemyDistToCentreRank = max(3 - whiteKingRank, whiteKingRank - 4)
            EnemyDistFromCentre = EnemyDistToCentreFile + EnemyDistToCentreRank
        else:
            EnemyDistToCentreFile = max(3 - blackKingFile, blackKingFile - 4)
            EnemyDistToCentreRank = max(3 - blackKingRank, blackKingRank - 4)
            EnemyDistFromCentre = EnemyDistToCentreFile + EnemyDistToCentreRank
        eval += EnemyDistFromCentre

        fileDist = abs(blackKingFile - whiteKingFile)
        rankDist = abs(blackKingRank - whiteKingRank)
        kingDist = fileDist + rankDist
        eval += 14 - kingDist
        # if (isWhite == False):
        #     eval = -eval
        return int(eval * endgameWeight)

    def evaluate(self, isWhite: bool) -> float:
        """
        evaluate evaluates the position solely based on the pieces points
        """
        materialValue = 0
        squares = list(self.board.keys())
        if (self.pythonBoard.is_stalemate()):
            return 0
        if (self.pythonBoard.outcome() != None):
            if (self.pythonBoard.outcome().winner == True):
                    return float('inf')
            elif (self.pythonBoard.outcome().winner == False):
                return float('-inf')
        for square in squares:
            # if there's a piece on the square
            if (self.board[square] != '0'):
                name = self.board[square]
                if (name.islower()):
                    color = "black"
                else:
                    color = "white"
                moves = set()
                piece = Piece(name, color, 0, moves)
                materialValue += piece.value * 10
        if (isWhite):
            endGameBonus = self.endGameEval(16 - self.whitePieces, isWhite)
        else:
            endGameBonus = self.endGameEval(16 - self.blackPieces, isWhite)
        return materialValue + endGameBonus

    def isCapture(self, square: str) -> bool:
        if (self.board[square] != '0'):
            return True
        else:
            return False

    def findCaptureMoves(self, allMoves: list[ch.Move], currPos: str) -> set[str]:
        """
        Finds all capture moves of the piece at currPos which is a string representing 
        a square on the board, such as a8 using allMoves which is a list containing 
        every legal move of every piece
        """
        legalMoves = set()
        for location in allMoves:
            pos = str(location)[2:4]
            try:
                # add move if it's legal
                if (ch.Move.from_uci(currPos + pos) in allMoves and self.board[pos] != '0'):
                    legalMoves.add(pos)
            except ch.InvalidMoveError:
                pass
        return legalMoves

    def searchCaptures(self, whiteTurn: bool, alpha: int, beta: int) -> float:
        """
        Search captures looks at sequences of immediate captures to ensure that
        the score given to the position is accurate even after the depth has ran out.
        It inherits alpha and beta from the search function as well as whiteTurn.
        """
        evaluation = self.evaluate(whiteTurn)
        squares = list(self.board.keys())
        possibleMoves = {}
        end = False
        if (whiteTurn):
            bestEvaluation = float('-inf')
            alpha = max(alpha, evaluation)
            if (alpha >= beta):
                return alpha
            for square in squares:
                if (self.board[square] != '0' and self.board[square].isupper()):
                    possibleMoves[square] = self.orderMoves(self.findCaptureMoves(self.pythonBoard.legal_moves, square), square)
            whiteSquares = list(possibleMoves.keys())
            for whiteSquare in whiteSquares:
                for move in possibleMoves[whiteSquare]:
                    self.pythonBoard.push(ch.Move.from_uci(whiteSquare + move))
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    # self.updateBoard(whiteSquare, move)
                    evaluation = self.searchCaptures(not whiteTurn, alpha, beta)
                    if (evaluation > bestEvaluation):
                        bestEvaluation = evaluation
                    self.pythonBoard.pop()
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    # self.updateBoard(move, whiteSquare)
                    alpha = max(alpha, evaluation)
                    if (beta <= alpha):
                        end = True
                        break
                if (end):
                    break
        else:
            bestEvaluation = float('inf')
            beta = min(beta, evaluation)
            if (alpha >= beta):
                return beta
            for square in squares:
                if (self.board[square] != '0' and self.board[square].isupper()):
                    possibleMoves[square] = self.orderMoves(self.findCaptureMoves(self.pythonBoard.legal_moves, square), square)
            blackSquares = list(possibleMoves.keys())
            for blackSquare in blackSquares:
                for move in possibleMoves[blackSquare]:
                    self.pythonBoard.push(ch.Move.from_uci(blackSquare + move))
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    # self.updateBoard(blackSquare, move)
                    evaluation = self.searchCaptures(not whiteTurn, alpha, beta)
                    if (evaluation < bestEvaluation):
                        bestEvaluation = evaluation
                    self.pythonBoard.pop()
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    # self.updateBoard(move, blackSquare)
                    beta = min(beta, evaluation)
                    if (beta <= alpha):
                        end = True
                        break
                if (end):
                    break
        return evaluation


    def search(self, depth: int, whiteTurn: bool, alpha: int, beta: int) -> float:
        """
        search function will give scores to position after searching with a
        depth of depth.
        """
        possibleMoves = {}
        end = False
        squares = list(self.board.keys())
        # end of depth
        if (depth == 0):
            return self.searchCaptures(whiteTurn, alpha, beta)
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
                    fenBoard = self.pythonBoard.board_fen()
                    self.board = fenConverter(fenBoard)
                    self.updateBoard(whiteSquare, move)

                    if (self.transpositions[(fenBoard, whiteTurn)][0] != None and self.transpositions[(fenBoard, whiteTurn)][1] > depth):
                        evaluation = self.transpositions[(fenBoard, whiteTurn)][0]
                        if (evaluation > bestEvaluation):
                            bestEvaluation = evaluation
                        self.pythonBoard.pop()
                        self.board = fenConverter(self.pythonBoard.board_fen())
                        alpha = max(alpha, evaluation)
                        if (beta <= alpha):
                            end = True
                            break
                        continue

                    evaluation = self.search(depth - 1, not whiteTurn, alpha, beta) # alpha best for white, beta best for black
                    if (self.transpositions[(fenBoard, whiteTurn)][0] == None):
                        self.transpositions[(fenBoard, whiteTurn)] = [evaluation, depth]
                    if (evaluation > bestEvaluation):
                        bestEvaluation = evaluation
                    self.pythonBoard.pop()
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    # self.updateBoard(move, whiteSquare)
                    alpha = max(alpha, evaluation)
                    # Pruning
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
            bestEvaluation = float('inf')
            blackSquares = list(possibleMoves.keys())
            # go through all possible moves of each black piece
            for blackSquare in blackSquares:
                for move in possibleMoves[blackSquare]:
                    self.pythonBoard.push(ch.Move.from_uci(blackSquare + move))
                    fenBoard = self.pythonBoard.board_fen()
                    self.board = fenConverter(fenBoard)
                    if (depth == DEPTH):
                        print(self.pythonBoard, '\n')
                    if (self.pythonBoard.is_checkmate() and depth == DEPTH):
                        print("CHECKMATE")
                        self.move = ch.Move.from_uci(blackSquare + move)
                        self.pythonBoard.pop()
                        return float('-inf')

                    if (self.transpositions[(fenBoard, whiteTurn)][0] != None and self.transpositions[(fenBoard, whiteTurn)][1] > depth):
                        evaluation = self.transpositions[(fenBoard, whiteTurn)][0]
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
                        continue

                    evaluation = self.search(depth - 1, not whiteTurn, alpha, beta)
                    if (self.transpositions[(fenBoard, whiteTurn)] == None):
                        self.transpositions[(fenBoard, whiteTurn)] = [evaluation, depth]
                    # if we get better score
                    if (evaluation < bestEvaluation):
                        bestEvaluation = evaluation
                        # Choose the move. Only legal moves for the next turn will be at depth DEPTH
                        if (depth == DEPTH):
                            self.move = ch.Move.from_uci(blackSquare + move)
                            self.materialValue = bestEvaluation
                    self.pythonBoard.pop()
                    self.board = fenConverter(self.pythonBoard.board_fen())
                    # self.updateBoard(move, blackSquare)
                    beta = min(beta, evaluation)
                    if (beta < alpha):
                        end = True
                        break
                if (end):
                    break
            return bestEvaluation
