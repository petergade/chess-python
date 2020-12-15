from __future__ import annotations
from typing import Tuple, List
from abc import ABC, abstractmethod
import enum

class Color(enum.Enum):
    WHITE = 0,
    BLACK = 1


WHITE = Color.WHITE
BLACK = Color.BLACK


class PieceType(enum.Enum):
    PAWN = enum.auto(),
    KNIGHT = enum.auto(),
    BISHOP = enum.auto(),
    ROOK = enum.auto(),
    QUEEN = enum.auto(),
    KING = enum.auto()


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, from_square: Tuple[int, int], to_square: Tuple[int, int], board) -> None:
        self.from_row = from_square[0]
        self.from_col = from_square[1]
        self.to_row = to_square[0]
        self.to_col = to_square[1]
        self.piece_moved: Piece = board[self.from_row][self.from_col]
        self.piece_captured: Piece = board[self.to_row][self.to_col]

    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return hash(self) == hash(other)
        return False

    def __hash__(self) -> int:
        return self.from_row * 1000 + self.from_col * 100 + self.to_row * 10 + self.to_col  # pro porovnavani tahu

    def __str__(self) -> str:
        return self.get_chess_notation()

    def get_chess_notation(self) -> str:
        return self.get_rank_file(self.from_row, self.from_col) + self.get_rank_file(self.to_row, self.to_col)

    def get_rank_file(self, row: int, column: int) -> str:
        return self.cols_to_files[column] + self.rows_to_ranks[row]


class Piece(ABC):

    # abstraktni property, musi vyplnit potomek
    @property
    def piece_type(self) -> PieceType:
        raise NotImplementedError

    # abstraktni property, musi vyplnit potomek
    @property
    def symbol(self) -> str:
        raise NotImplementedError

    def __init__(self, color: Color):
        self.color = color

    def __str__(self) -> str:
        return f'{"w" if self.color == WHITE else "b"}{self.symbol}'

    @abstractmethod
    def generate_pseudo_legal_moves(self, r: int, c: int, board: List[List[Piece]]) -> List[Move]:
        pass

    '''
     metoda pro generovani tahu po diagonalach, je dana takto obecne, aby mohla byt pouzita na generovani tahu strelce 
     a damy
    '''
    @staticmethod
    def generate_pseudo_legal_diagonal_moves(r: int, c: int, color: Color, board: List[List[Piece]], up: bool,
                                             left: bool) -> List[Move]:
        moves = []
        i = 1
        while True:
            new_row = r - i if up else r + i
            new_column = c - i if left else c + i
            if new_row < 0 or new_row > 7 or new_column < 0 or new_column > 7:
                return moves
            new_piece = board[new_row][new_column]
            if new_piece is None or new_piece.color != color:
                moves.append(Move((r, c), (new_row, new_column), board))
            if new_piece is None:
                i += 1
            else:
                return moves

    '''
    metoda pro generovani tahu po primkach, je dana takto obecne, aby mohla byt pouzita na generovani tahu veze a damy
    '''
    @staticmethod
    def generate_pseudo_legal_straight_moves(r: int, c: int, color: Color, board: List[List[Piece]], vertical: bool,
                                             positive: bool) -> List[Move]:
        moves = []
        i = 1
        while True:
            new_row = r if not vertical else r + i if positive else r - i
            new_column = c if vertical else c + i if positive else c - i
            if new_row < 0 or new_row > 7 or new_column < 0 or new_column > 7:
                return moves
            new_piece = board[new_row][new_column]
            if new_piece is None or new_piece.color != color:
                moves.append(Move((r, c), (new_row, new_column), board))
            if new_piece is None:
                i += 1
            else:
                return moves


class Pawn(Piece):
    piece_type = PieceType.PAWN
    symbol = 'p'

    def generate_pseudo_legal_moves(self, r: int, c: int, board: List[List[Piece]]) -> List[Move]:
        moves: List[Move] = []
        if self.color == WHITE:
            # kontrola, zda je mozny posun o jedno pole dopredu
            if board[r - 1][c] is None:
                moves.append(Move((r, c), (r - 1, c), board))
                # kontrola, zda je mozny posun o dve pole dopredu
                if r == 6 and board[r - 2][c] is None:
                    moves.append(Move((r, c), (r - 2, c), board))
            if c < 7:  # brani doprava
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if board[r - 1][c + 1] is not None and board[r - 1][c + 1].color == BLACK:
                    moves.append(Move((r, c), (r - 1, c + 1), board))
            if c > 0:  # brani doleva
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if board[r - 1][c - 1] is not None and board[r - 1][c - 1].color == BLACK:
                    moves.append(Move((r, c), (r - 1, c - 1), board))
        else:
            # kontrola, zda je mozny posun o jedno pole dopredu
            if board[r + 1][c] is None:
                moves.append(Move((r, c), (r + 1, c), board))
                # kontrola, zda je mozny posun o dve pole dopredu
                if r == 1 and board[r + 2][c] is None:
                    moves.append(Move((r, c), (r + 2, c), board))
            if c < 7:  # brani doprava
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if board[r + 1][c + 1] is not None and board[r + 1][c + 1].color == WHITE:
                    moves.append(Move((r, c), (r + 1, c + 1), board))
            if c > 0:  # brani doleva
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if board[r + 1][c - 1] is not None and board[r + 1][c - 1].color == WHITE:
                    moves.append(Move((r, c), (r + 1, c - 1), board))
        return moves


class Rook(Piece):
    piece_type = PieceType.ROOK
    symbol = 'R'

    def generate_pseudo_legal_moves(self, r: int, c: int, board: List[List[Piece]]) -> List[Move]:
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, True, True) or [])
        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, True, False) or [])
        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, False, True) or [])
        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, False, False) or [])

        return moves


class Knight(Piece):
    piece_type = PieceType.KNIGHT
    symbol = 'N'

    '''
    Generuje vsechny kandidaty na tahy pro jezdce. Zde musime prozkoumat vsech 8 moznych poli, kam muze jezdec tahnout
    '''
    def generate_pseudo_legal_moves(self, r: int, c: int, board: List[List[Piece]]) -> List[Move]:
        moves: List[Move] = []

        # doleva a nahoru
        if r - 1 >= 0 and c - 2 >= 0 and (board[r - 1][c - 2] is None or board[r - 1][c - 2].color != self.color):
            moves.append(Move((r, c), (r - 1, c - 2), board))

        # nahoru a doleva
        if r - 2 >= 0 and c - 1 >= 0 and (board[r - 2][c - 1] is None or board[r - 2][c - 1].color != self.color):
            moves.append(Move((r, c), (r - 2, c - 1), board))

        # doprava a nahoru
        if r - 1 >= 0 and c + 2 <= 7 and (board[r - 1][c + 2] is None or board[r - 1][c + 2].color != self.color):
            moves.append(Move((r, c), (r - 1, c + 2), board))

        # nahoru a doprava
        if r - 2 >= 0 and c + 1 <= 7 and (board[r - 2][c + 1] is None or board[r - 2][c + 1].color != self.color):
            moves.append(Move((r, c), (r - 2, c + 1), board))

        # doleva a dolu
        if r + 1 <= 7 and c - 2 >= 0 and (board[r + 1][c - 2] is None or board[r + 1][c - 2].color != self.color):
            moves.append(Move((r, c), (r + 1, c - 2), board))

        # dolu a doleva
        if r + 2 <= 7 and c - 1 >= 0 and (board[r + 2][c - 1] is None or board[r + 2][c - 1].color != self.color):
            moves.append(Move((r, c), (r + 2, c - 1), board))

        # doprava a dolu
        if r + 1 <= 7 and c + 2 <= 7 and (board[r + 1][c + 2] is None or board[r + 1][c + 2].color != self.color):
            moves.append(Move((r, c), (r + 1, c + 2), board))

        # dolu a doprava
        if r + 2 <= 7 and c + 1 <= 7 and (board[r + 2][c + 1] is None or board[r + 2][c + 1].color != self.color):
            moves.append(Move((r, c), (r + 2, c + 1), board))

        return moves


class Bishop(Piece):
    piece_type = PieceType.BISHOP
    symbol = 'B'

    def generate_pseudo_legal_moves(self, r: int, c: int, board: List[List[Piece]]) -> List[Move]:
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, True, True) or [])
        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, True, False) or [])
        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, False, True) or [])
        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, False, False) or [])

        return moves


class Queen(Piece):
    piece_type = PieceType.QUEEN
    symbol = 'Q'

    '''
    Generuje vsechny kandidaty na tahy pro damu. Je to kombinace tahu, ktere muze delat vez a strelec, tedy rovne
    tahy a diagonalni tahy
    '''
    def generate_pseudo_legal_moves(self, r: int, c: int, board: List[List[Piece]]) -> List[Move]:
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, True, True) or [])
        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, True, False) or [])
        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, False, True) or [])
        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, self.color, board, False, False) or [])

        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, True, True) or [])
        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, True, False) or [])
        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, False, True) or [])
        moves.extend(Piece.generate_pseudo_legal_straight_moves(r, c, self.color, board, False, False) or [])

        return moves


class King(Piece):
    piece_type = PieceType.KING
    symbol = 'K'

    '''
    Generuje vsechny kandidaty na tahy pro krale. Zde musime prozkoumat vsech 8 moznych poli, kam muze kral tahnout
    '''
    def generate_pseudo_legal_moves(self, r: int, c: int, board: List[List[Piece]]) -> List[Move]:
        moves: List[Move] = []

        # doleva nahoru
        if r - 1 >= 0 and c - 1 >= 0 and (board[r - 1][c - 1] is None or board[r - 1][c - 1].color != self.color):
            moves.append(Move((r, c), (r - 1, c - 1), board))

        # nahoru
        if r - 1 >= 0 and (board[r - 1][c] is None or board[r - 1][c].color != self.color):
            moves.append(Move((r, c), (r - 1, c), board))

        # doprava nahoru
        if r - 1 >= 0 and c + 1 <= 7 and (board[r - 1][c + 1] is None or board[r - 1][c + 1].color != self.color):
            moves.append(Move((r, c), (r - 1, c + 1), board))

        # doprava
        if c + 1 <= 7 and (board[r][c + 1] is None or board[r][c + 1].color != self.color):
            moves.append(Move((r, c), (r, c + 1), board))

        # doprava dolu
        if r + 1 <= 7 and c + 1 <= 7 and (board[r + 1][c + 1] is None or board[r + 1][c + 1].color != self.color):
            moves.append(Move((r, c), (r + 1, c + 1), board))

        # dolu
        if r + 1 <= 7 and (board[r + 1][c] is None or board[r + 1][c].color != self.color):
            moves.append(Move((r, c), (r + 1, c), board))

        # doleva dolu
        if r + 1 <= 7 and c - 1 >= 0 and (board[r + 1][c - 1] is None or board[r + 1][c - 1].color != self.color):
            moves.append(Move((r, c), (r + 1, c - 1), board))

        # doleva
        if c - 1 >= 0 and (board[r][c - 1] is None or board[r][c - 1].color != self.color):
            moves.append(Move((r, c), (r, c - 1), board))

        return moves


class ChessGame:
    def __init__(self) -> None:
        self.board: List[List[Piece]] = [
            [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK), King(BLACK), Bishop(BLACK), Knight(BLACK),
             Rook(BLACK)],
            [Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
             Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
             Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)],
            [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE), King(WHITE), Bishop(WHITE), Knight(WHITE),
             Rook(WHITE)]]
        self.white_to_move: bool = True
        self.move_stack: List[Move] = []

    '''
    Metoda provadi tah. Uvolni puvodni pole a na cilove pole umisti figuru, ktera tahne. Tah se ulozi do seznamu tahu.
    Pote se prehodi hrac, ktery je na tahu.
    '''

    def make_move(self, move: Move) -> None:
        self.board[move.from_row][move.from_col] = None
        self.board[move.to_row][move.to_col] = move.piece_moved
        self.move_stack.append(move)  # ulozime si tah, abychom ho pozdeji mohli vratit
        self.white_to_move = not self.white_to_move  # zmenime hrace, ktery je na tahu

    '''
    Metoda vraci tah. Tah si vezme ze seznamu tahu, vyhozenou figuru (pokud nejaka je) vrati zpatky a figuru, 
    ktera tahla vrati na puvodni pole. Dale prehodi hrace, ktery je na tahu.
    '''

    def undo_move(self) -> None:
        if len(self.move_stack) == 0:
            pass
        move = self.move_stack.pop()
        self.board[move.from_row][move.from_col] = move.piece_moved
        self.board[move.to_row][move.to_col] = move.piece_captured
        self.white_to_move = not self.white_to_move  # zmenime hrace, ktery je na tahu

    '''
    Metoda si nejdrive zjisti vsechny pseudo-legalni tahy volanim metody get_pseudo_legal_moves a pote kontroluje kazdy
    z nich tak, ze si vygeneruje vsechny mozne odpovedi soupere a zjisti, jestli by souper mohl nekterym tahem sebrat 
    krale a pokud ano, takovy tah vylouci. Pote vrati uz pouze seznam legalnich tahu
    '''

    def get_legal_moves(self) -> List[Move]:
        return self.generate_pseudo_legal_moves()

    '''
    Metoda generuje vsechny mozne tahy hrace na tahu s tim, ze se nekontroluje, zda by se hrac na tahu nedostal do sachu.
    Tuto kontrolu provadi az metoda get_legal_moves
    '''

    def generate_pseudo_legal_moves(self) -> List[Move]:
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece is not None:
                    color = piece.color
                    if (color == WHITE and self.white_to_move) or (color == BLACK and not self.white_to_move):
                        moves.extend(piece.generate_pseudo_legal_moves(r, c, self.board) or [])
        return moves

    def print_pieces(self, rank: int) -> None:
        s = '  '
        for file in range(len(self.board[rank])):
            piece = self.board[rank][file]
            if piece is None:
                s += '|     '
            else:
                s += f'|{str(piece).center(5, " ")}'
        s += '|'
        print(s)

    def print_square_colors(self, rank: int) -> None:
        s = f'{rank + 1} '
        for file in range(len(self.board[rank])):
            color = BLACK if (rank + file) % 2 == 0 else WHITE
            if color == WHITE:
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
        for rank in range(self.board):
            self.print_rank(rank)
        print('  |-----|-----|-----|-----|-----|-----|-----|-----|')
        print('     A     B     C     D     E     F     G     H   ')


class ConsoleGame:

    # udelej tah (predej do dale do tridy Board)
    def do_move(self, move):
        if self.board.do_move(move):
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
        chess_game = ChessGame()
        self.board.print_board()
        choice = ''

        while choice != 'q':
            self.display_main_menu()
            choice = input("what would you like to do? ")

            # Respond to the user's choice.
            if choice == '1':
                move_uci = input('Enter you move: ')
                print(f'Your move is {move_uci}')
                move = Move.from_uci(move_uci)
                if move is None:
                    # spatne zapsany tah
                    pass
                if not self.do_move(move, self.color_in_turn):
                    # neplatny tah
                    pass
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

    @staticmethod
    def display_main_menu():
        print('[1] - Input next move')
        print('[2] - Display all moves already played')
        print('[3] - Replay the game from the beginning')
        print('[4] - Print legal moves')
        print('[q] - Quit app')


if __name__ == '__main__':
    game = ConsoleGame()
    game.start()
    print('Program finished')
