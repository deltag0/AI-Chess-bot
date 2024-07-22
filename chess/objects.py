import os

class Piece:
    """
    Class to keep track of pieces and important values associated with them
    """
    def __init__(self, name: str, color: str, value: int, moves: set, texture=None, texture_rect=None):
        self.name = name
        # if the piece is black, then we want to minimize its score, otherwise, we want to maximize it
        if (self.name.islower()):
            value_sign = -1
        else:
            value_sign = 1
        # associate a numerical value with the piece, for exame a queen would be worth 9 points
        if (self.name == 'p' or self.name == 'P'):
            self.value = 1
        elif (self.name == 'n' or self.name == 'N'):
            self.value = 3
        elif (self.name == 'b' or self.name == 'B'):
            self.value = 3.01
        elif (self.name == 'r' or self.name == 'R'):
            self.value = 5
        elif (self.name == 'q' or self.name == 'Q'):
            self.value = 9
        elif (self.name == 'k' or self.name == 'K'):
            self.value = 10000
        # give the piece the name commonly called
        if (self.name == 'p'):
            self.name = 'black_pawn'
        if (self.name == 'P'):
            self.name = 'white_pawn'
        if (self.name == 'n'):
            self.name = 'black_knight'
        if (self.name == 'N'):
            self.name = 'white_knight'
        if (self.name == 'b'):
            self.name = 'black_bishop'
        if (self.name == 'B'):
            self.name = 'white_bishop'
        if (self.name == 'r'):
            self.name = 'black_rook'
        if (self.name == 'R'):
            self.name = 'white_rook'
        if (self.name == 'q'):
            self.name = 'black_queen'
        if (self.name == 'Q'):
            self.name = 'white_queen'
        if (self.name == 'k'):
            self.name = 'black_king'
        if (self.name == 'K'):
            self.name = 'white_king'
        self.color = color
        self.moved = False
        self.value = self.value * value_sign
        self.moves = moves
        self.texture = texture
        self.set_texture('80')
        self.texture_rect = texture_rect

    def set_texture(self, size:str) -> None:
        """
        Give the path name to the picture of the piece, so we can load it as an image
        """
        self.texture = os.path.join(
            f"assets/{size}px/{self.name}.png"
        )
