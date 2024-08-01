from objects import Piece
from board import findLegalMoves
import chess as ch
from constants import *
from collections import defaultdict
from heatmaps import *

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
    def __init__(self, board: dict[str: str], pythonBoard: ch.Board, whitePieces: int, blackPieces: int, transpositions: defaultdict, prevDepthScores: defaultdict,
                 whitePieceCount: dict[str: int], blackPieceCount: dict[str: int]) -> None:
        self.board = board
        self.pythonBoard = pythonBoard
        self.materialValue = 0
        self.move = None
        self.transpositions = transpositions
        self.whitePieces = whitePieces
        self.blackPieces = blackPieces
        self.prevDepthScores = prevDepthScores
        self.whitePieceCount = whitePieceCount
        self.blackPieceCount = blackPieceCount

    def attackedByPawn(self, start: str, color: str) -> bool:
        """
        attackedByPawn detects if a piece at position start with the color color is attacked by a pawn.
        A pinned pawn will not count as an attacker.
        """
        if (color == "white"):
            left = ""
            right = ""
            # check row
            if (start[1] != '8'):
                # check column (pawns on extremes can only capture in 1 direction)
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
        move is. There are 4 criterias: 
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
            if (self.pythonBoard.is_checkmate()):
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
        return combined

    def endGameEval(self, endgameWeight: float, isWhite: bool) -> int:
        """
        endGameEval gives a higher score to moves that force the enemy 
        king to the backRanks when the game is closer to the end.
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

        return int(eval * endgameWeight)

    def evaluate(self, isWhite: bool) -> float:
        """
        evaluate evaluates the position
        """
        materialValue = 0
        squares = list(self.board.keys())
        if (self.pythonBoard.is_stalemate()):
            return 0
        if (self.pythonBoard.outcome() != None):
            if (self.pythonBoard.outcome().winner == True and isWhite == False):
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
                if color == 'black':
                    if name == 'p':
                        vMap = pawnMap(square)
                        materialValue += vMap.mapValue()
                    elif name == 'n':
                        vMap = knightMap(square)
                        materialValue += vMap.mapValue()
                    elif name == 'b':
                        vMap = bishopMap(square)
                        materialValue += vMap.mapValue()
                    elif name == 'q':
                        vMap = queenMap(square)
                        materialValue += vMap.mapValue()
                    elif name == 'k':
                        if ((self.whitePieceCount['Q'] == 0 and self.whitePieceCount['R'] == 1 and self.whitePieceCount['B'] + self.whitePieceCount['N'] <= 2) or
                            (self.whitePieceCount['B'] + self.whitePieceCount['N'] + self.whitePieceCount['R'] <= 2 and self.whitePieceCount['R'] <= 1)):
                            vMap = lateKingMap(square)
                        else:
                            vMap = earlyKingMap(square)
                        materialValue += vMap.mapValue()
                    elif name == 'r':
                        vMap = rookMap(square)
                        materialValue += vMap.mapValue()
                if color == 'white':
                    row = int(square[1])
                    newRow = str(9 - row)
                    square = square[0] + newRow
                    if name == 'P':
                        vMap = pawnMap(square)
                        materialValue += -vMap.mapValue()
                    elif name == 'N':
                        vMap = knightMap(square)
                        materialValue += -vMap.mapValue()
                    elif name == 'B':
                        vMap = bishopMap(square)
                        materialValue += -vMap.mapValue()
                    elif name == 'Q':
                        vMap = queenMap(square)
                        materialValue += -vMap.mapValue()
                    elif name == 'K':
                        if ((self.blackPieceCount['q'] == 0 and self.blackPieceCount['r'] == 1 and self.blackPieceCount['b'] + self.blackPieceCount['n'] <= 2) or
                            (self.blackPieceCount['b'] + self.blackPieceCount['n'] + self.blackPieceCount['r'] <= 2 and self.blackPieceCount['r'] <= 1)):
                            vMap = lateKingMap(square)
                        else:
                            vMap = earlyKingMap(square)
                        materialValue += -vMap.mapValue()
                    elif name == 'R':
                        vMap = rookMap(square)
                        materialValue += -vMap.mapValue()
                materialValue += piece.value * 10

        if isWhite:
            return materialValue
        else:
            return -materialValue

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
        moves = []
        evaluation = self.evaluate(whiteTurn)
        squares = list(self.board.keys())
        possibleMoves = {}
        # don't need to check moves
        if evaluation >= beta:
                return beta
        alpha = max(alpha, evaluation)
        if whiteTurn:
            for square in squares:
                if (self.board[square] != '0' and findColor(self.board[square]) == "white"):
                    squareMoves = self.orderMoves(self.findCaptureMoves(self.pythonBoard.legal_moves, square), square)
                    for move, score in squareMoves:
                        moves.append([ch.Move.from_uci(square + move), score])
            moves = [move[0] for move in sorted(moves, key=lambda x: x[1], reverse=True)]
        else:
            for square in squares:
                if (self.board[square] != '0' and findColor(self.board[square]) == "black"):
                    squareMoves = self.orderMoves(self.findCaptureMoves(self.pythonBoard.legal_moves, square), square)
                    for move, score in squareMoves:
                        moves.append([ch.Move.from_uci(square + move), score])
            moves = [move[0] for move in sorted(moves, key=lambda x: x[1], reverse=True)]

        for move in moves:
            self.pythonBoard.push(move)
            self.board = fenConverter(self.pythonBoard.board_fen())
            evaluation = -self.searchCaptures(not whiteTurn, -beta, -alpha)
            self.pythonBoard.pop()
            self.board = fenConverter(self.pythonBoard.board_fen())
            if evaluation >= beta:
                return beta
            alpha = max(alpha, evaluation)
        return alpha

    def search(self, depth: int, whiteTurn: bool, alpha: int, beta: int, baseDepth: int) -> float:
        """
        search function will give scores to position after searching with a
        depth of depth.
        """
        squares = list(self.board.keys())
        # end of depth
        if (depth == 0):
            return self.searchCaptures(whiteTurn, alpha, beta)

        moves = []
        # finding legal moves this turn
        if (whiteTurn):
            for square in squares:
                # check for a piece
                if (self.board[square] != '0' and self.board[square].isupper()):
                    squareMoves = self.orderMoves(findLegalMoves(self.pythonBoard.legal_moves, square), square)
                    for move, score in squareMoves:
                        moves.append([ch.Move.from_uci(square + move), score])
            moves = [move[0] for move in sorted(moves, key=lambda x: x[1], reverse=True)]

        else:
            # organize the moves based on the past search at lower depth
            if baseDepth != 1 and depth == baseDepth:
                squareMoves = list(zip(self.prevDepthScores.keys(), self.prevDepthScores.values()))
                moves = [ch.Move.from_uci(move[0]) for move in sorted(squareMoves, key=lambda x: x[1])]
            else:
                for square in squares:
                    if (self.board[square] != '0' and self.board[square].islower()):
                        squareMoves = self.orderMoves(findLegalMoves(self.pythonBoard.legal_moves, square), square)
                        for move, score in squareMoves:
                            moves.append([ch.Move.from_uci(square + move), score])
                moves = [move[0] for move in sorted(moves, key=lambda x: x[1], reverse=True)]
        print([move.uci() for move in moves])
        for move in moves:
            self.pythonBoard.push(move)
            fenBoard = self.pythonBoard.board_fen()
            self.board = fenConverter(fenBoard)

            if (self.pythonBoard.is_checkmate() and depth == baseDepth):
                self.move = move
                self.pythonBoard.pop()
                return float('-inf')
            # if we find a position we've already visited at higher or equal depth, no need to re-evaluate
            if (self.transpositions[(fenBoard, whiteTurn)][0] != None and self.transpositions[(fenBoard, whiteTurn)][1] >= depth):
                evaluation = self.transpositions[(fenBoard, whiteTurn)][0]
                self.pythonBoard.pop()
                self.board = fenConverter(self.pythonBoard.board_fen())
                if depth == baseDepth:
                    self.prevDepthScores[move.uci()] = evaluation
                if evaluation >= beta:
                    return beta
                if evaluation > alpha:
                    if depth == baseDepth:
                        self.move = move
                        self.materialValue = alpha
                    alpha = evaluation
                continue

            evaluation = -self.search(depth - 1, not whiteTurn, -beta, -alpha, baseDepth)
            self.transpositions[(fenBoard, whiteTurn)] = [evaluation, depth]

            # adding moves for our moves this depth
            if depth == baseDepth:
                self.prevDepthScores[move.uci()] = evaluation

            self.pythonBoard.pop()
            self.board = fenConverter(self.pythonBoard.board_fen())

            # pruning
            if evaluation >= beta:
                return beta

            if evaluation > alpha:
                # Choose the move. Only legal moves for the next turn will be at depth baseDepth
                if (depth == baseDepth):
                    self.move = move
                    self.materialValue = alpha
                alpha = evaluation
        return alpha
