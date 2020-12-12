from abc import ABC, abstractmethod
import enum
from typing import Optional, Iterator, Dict, List
import unicodedata


PIECE_SYMBOLS = [None, "p", "n", "b", "r", "q", "k"]


class Color(enum.Enum):
    WHITE = 0,
    BLACK = 1


class PieceType(enum.Enum):
    PAWN = enum.auto(),
    KNIGHT = enum.auto(),
    BISHOP = enum.auto(),
    ROOK = enum.auto(),
    QUEEN = enum.auto(),
    KING = enum.auto()


Square = int

FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h"]
RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8"]
SQUARE_NAMES = [f + r for r in RANK_NAMES for f in FILE_NAMES]


def get_square(square_str) -> Square:
    return SQUARE_NAMES.index(square_str.lower())

def get_square_name(square: Square) -> str:
    return SQUARE_NAMES[square]


def get_file_name(i: int) -> str:
    return FILE_NAMES[i]


class Move:

    def __init__(self, from_square: Square, to_square: Square, promotion_type = None):
        self.from_square = from_square
        self.to_square = to_square
        self.promotion_type = promotion_type

    def __str__(self):
        return self.to_uci()

    def to_uci(self):
        return f'{get_square_name(self.from_square)}{get_square_name(self.to_square)}'

    @classmethod
    def from_uci(cls, uci: str):
        if 4 <= len(uci) <= 5:
            from_square = get_square(uci[0:2])
            to_square = get_square(uci[2:4])
            promotion = PIECE_SYMBOLS.index(uci[4]) if len(uci) == 5 else None
            if from_square == to_square:
                raise ValueError(f"invalid move")
            return Move(from_square, to_square, promotion=promotion)
        else:
            raise ValueError(f"expected uci string to be of length 4 or 5: {uci!r}")


class Piece(ABC):

    piece_type: PieceType

    def __init__(self, color: Color, square: Square):
        self.color = color
        self.square = square
        self.is_killed = False

    def __str__(self) -> str:
        return self.symbol()

    def symbol(self) -> str:
        return self.get_symbol() if self.color == Color.WHITE else f'.{self.get_symbol()}.'

    @abstractmethod
    def get_symbol(self) -> str:
        pass

    @abstractmethod
    def generate_pseudo_legal_moves(self) -> List[Move]:
        pass


class Pawn(Piece):
    piece_type = PieceType.PAWN

    def get_symbol(self) -> str:
        return 'p'

    def generate_pseudo_legal_moves(self, pieces: List[Piece]) -> List[Move]:
        pseudo_legal_moves = []
        occupies_squares = Board.get_occupied_squares(pieces)
        if self.color == Color.WHITE:
            # tah ze zakladniho postaveni
            if 8 <= self.square <= 16:
                possible_square = self.square + 16
                if possible_square not in occupies_squares:
                    pseudo_legal_moves.append(Move(self.square, possible_square))
        else:
            # tah ze zakladniho postaveni
            if 48 <= self.square <= 56:
                possible_square = self.square - 16
                if possible_square not in occupies_squares:
                    pseudo_legal_moves.append(Move(self.square, possible_square))

        return pseudo_legal_moves


class King(Piece):
    piece_type = PieceType.KING

    def get_symbol(self) -> str:
        return 'K'

    def generate_pseudo_legal_moves(self, pieces: List[Piece]) -> List[Move]:
        return []


class Queen(Piece):
    piece_type = PieceType.QUEEN

    def get_symbol(self) -> str:
        return 'D'

    def generate_pseudo_legal_moves(self, pieces: List[Piece]) -> List[Move]:
        return []


class Knight(Piece):
    piece_type = PieceType.KNIGHT

    def get_symbol(self) -> str:
        return 'J'

    def generate_pseudo_legal_moves(self, pieces: List[Piece]) -> List[Move]:
        return []


class Bishop(Piece):
    piece_type = PieceType.BISHOP

    def get_symbol(self) -> str:
        return 'S'

    def generate_pseudo_legal_moves(self, pieces: List[Piece]) -> List[Move]:
        return []


class Rook(Piece):
    piece_type = PieceType.ROOK

    def get_symbol(self) -> str:
        return 'V'

    def generate_pseudo_legal_moves(self, pieces: List[Piece]) -> List[Move]:
        return []


class Board:
    is_white_turn: bool = True
    pieces: Dict[int, Piece]

    def __init__(self):
        self.pieces = {}
        self.initialize_white_pieces()
        self.initialize_black_pieces()

    def __repr__(self):
        self.print_board()

    def initialize_white_pieces(self):
        for i in range(0, 8):
            square = get_square(f'{get_file_name(i)}{2}')
            self.pieces[square] = Pawn(Color.WHITE, square)
        self.pieces[get_square('a1')] = Rook(Color.WHITE, get_square('a1'))
        self.pieces[get_square('h1')] = Rook(Color.WHITE, get_square('h1'))
        self.pieces[get_square('b1')] = Knight(Color.WHITE, get_square('b1'))
        self.pieces[get_square('g1')] = Knight(Color.WHITE, get_square('g1'))
        self.pieces[get_square('c1')] = Bishop(Color.WHITE, get_square('c1'))
        self.pieces[get_square('f1')] = Bishop(Color.WHITE, get_square('f1'))
        self.pieces[get_square('e1')] = King(Color.WHITE, get_square('e1'))
        self.pieces[get_square('d1')] = Queen(Color.WHITE, get_square('d1'))

    def initialize_black_pieces(self):
        for i in range(0, 8):
            square = get_square(f'{get_file_name(i)}{7}')
            self.pieces[square] = Pawn(Color.BLACK, square)
        self.pieces[get_square('a8')] = Rook(Color.BLACK, get_square('a8'))
        self.pieces[get_square('h8')] = Rook(Color.BLACK, get_square('h8'))
        self.pieces[get_square('b8')] = Knight(Color.BLACK, get_square('b8'))
        self.pieces[get_square('g8')] = Knight(Color.BLACK, get_square('g8'))
        self.pieces[get_square('c8')] = Bishop(Color.BLACK, get_square('c8'))
        self.pieces[get_square('f8')] = Bishop(Color.BLACK, get_square('f8'))
        self.pieces[get_square('e8')] = King(Color.BLACK, get_square('e8'))
        self.pieces[get_square('d8')] = Queen(Color.BLACK, get_square('d8'))

    def generate_legal_moves(self, color_in_turn: Color) -> List[Move]:
        legal_moves = []

        for piece in [piece for piece in self.pieces.values() if piece.color == color_in_turn]:
            pseudo_legal_moves = piece.generate_pseudo_legal_moves(self.pieces)
            for pseudo_legal_move in pseudo_legal_moves:
                if self.is_legal_move(pseudo_legal_move):
                    legal_moves.append(pseudo_legal_move)
        return legal_moves

    def is_legal_move(self, pseudo_legal_move):
        return True

    def print_pieces(self, rank: int) -> None:
        s = '  '
        for file in range(0, 8):
            piece = self.pieces[(rank * 8) + file] if ((rank * 8) + file) in self.pieces else None
            if piece is None:
                s += '|     '
            elif piece.color == Color.WHITE:
                s += f'|{unicodedata.normalize("NFC", piece.symbol()).center(5, " ")}'
            else:
                s += f'| {piece} '
        s += '|'
        print(s)

    @staticmethod
    def get_occupied_squares(pieces: List[Piece]) -> List[Square]:
        return [square for square in pieces.keys()]

    @staticmethod
    def print_square_colors(rank: int) -> None:
        s = f'{rank + 1} '
        for file in range(0, 8):
            color = Color.BLACK if (rank + file) % 2 == 0 else Color.WHITE
            if color == Color.WHITE:
                s += '|    w'
            else:
                s += '|    b'
        s += '|'
        print(s)

    def print_rank(self, rank: int) -> None:
        print('  |-----|-----|-----|-----|-----|-----|-----|-----|')
        self.print_pieces(rank)
        self.print_square_colors(rank)

    def print_board(self) -> None:
        for rank in range(7, -1, -1):
            self.print_rank(rank)
        print('  |-----|-----|-----|-----|-----|-----|-----|-----|')
        print('     A     B     C     D     E     F     G     H   ')


class ChessGame:
    color_in_turn: Color = Color.WHITE
    moves: List[Move]

    def __init__(self):
        self.board = Board()

    # udelej tah (predej do dale do tridy Board)
    def do_move(self, move_uci):
        move = self.board.do_move(move_uci)
        if move is not None:
            self.moves.append(move)

    # zobrazeni zaznamu partie
    def print_all_moves(self):
        for move, i in self.moves:
            print('')

    # prehravani partie po pultazich
    def replay_game(self):
        for move, i in self.moves:
            print('')

    # navrat do pozice po poslednim tahu
    def go_to_latest_move(self):
        pass

    def start(self):
        print('Game started')
        self.board.print_board()
        choice = ''

        while choice != 'q':
            ConsoleHelpers.display_main_menu()
            choice = input("what would you like to do? ")

            # Respond to the user's choice.
            if choice == '1':
                move_uci = input('Enter you move: ')
                print(f'Your move is {move_uci}')
                self.do_move(move_uci)
                self.board.print_board()
            elif choice == '2':
                print("\nI can't wait to meet this person!\n")
            elif choice == '4':
                legal_moves = self.board.generate_legal_moves(self.color_in_turn)
                print(','.join(str(legal_move) for legal_move in legal_moves))
            elif choice == 'q':
                print("\nThanks for playing. Bye.")
            else:
                print("\nI didn't understand that choice.\n")


class ConsoleHelpers:
    @staticmethod
    def display_main_menu():
        print('[1] - Input next move')
        print('[2] - Display all moves already played')
        print('[3] - Replay the game from the beginning')
        print('[4] - Print legal moves')
        print('[q] - Quit app')


if __name__ == '__main__':
    chess_game = ChessGame()
    chess_game.start()
    print('Program finished')
