from __future__ import annotations
from typing import Tuple, List, Union
from abc import ABC, abstractmethod
import enum

import bcolors


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


PAWN = PieceType.PAWN
KNIGHT = PieceType.KNIGHT
BISHOP = PieceType.BISHOP
ROOK = PieceType.ROOK
QUEEN = PieceType.QUEEN
KING = PieceType.KING


# funkce vyuzivana pri promene pesce na jinou figuru
def create_piece(color: Color, piece_type: PieceType):
    return {
        BISHOP: Bishop(color),
        KNIGHT: Knight(color),
        ROOK: Rook(color),
        QUEEN: Queen(color)
    }[piece_type]


class GameResult(enum.Enum):
    WHITE_WIN = 0,
    BLACK_WIN = 1,
    STALEMATE = 2,
    THREEFOLD_REPETITION_DRAW = 3,
    FIFTY_MOVE_RULE_DRAW = 4,
    INSUFFICIENT_MATERIAL_DRAW = 5


class Move:
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}
    files = files_to_cols.keys()
    ranks = ranks_to_rows.keys()

    def __init__(self, from_square: Tuple[int, int], to_square: Tuple[int, int], board: List[List[Piece]],
                 promotion_type: PieceType = QUEEN, is_enpassant_move: bool = False) -> None:
        self.start_row: int = from_square[0]
        self.start_col: int = from_square[1]
        self.end_row: int = to_square[0]
        self.end_col: int = to_square[1]
        self.piece_moved: Piece = board[self.start_row][self.start_col]
        self.piece_captured: Piece = board[self.end_row][self.end_col]

        # promena pesce
        self.promotion_type: PieceType = promotion_type
        self.is_pawn_promotion: bool = (self.piece_moved.color == WHITE and self.piece_moved.piece_type == PAWN and
                                        self.end_row == 0) or \
                                       (self.piece_moved.color == BLACK and self.piece_moved.piece_type == PAWN and
                                        self.end_row == 7)

        # brani mimochodem
        self.is_enpassant_move: bool = is_enpassant_move
        if self.is_enpassant_move:
            if self.piece_moved.color == WHITE:
                self.piece_captured = board[self.end_row + 1][self.end_col]
            else:
                self.piece_captured = board[self.end_row - 1][self.end_col]

    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return hash(self) == hash(other)
        return False

    def __hash__(self) -> int:
        return self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col  # pro porovnavani tahu

    def __str__(self) -> str:
        return self.get_uci_chess_notation()

    def __repr__(self) -> str:
        return self.get_uci_chess_notation()

    def get_uci_chess_notation(self) -> str:
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_classic_chess_notation(self) -> str:
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row: int, column: int) -> str:
        return self.cols_to_files[column] + self.rows_to_ranks[row]

    @classmethod
    def from_uci(cls, uci: str, board: List[List[Piece]]) -> Move:
        if 4 <= len(uci) <= 5:
            from_square = uci[0:2]
            to_square = uci[2:4]

            if from_square[0] not in cls.files:
                raise ValueError('Neplatný tah - první znak může být pouze a-h')
            if from_square[1] not in cls.ranks:
                raise ValueError('Neplatný tah - druhý znak může být pouze 1-8')
            if to_square[0] not in cls.files:
                raise ValueError('Neplatný tah - třetí znak může být pouze a-h')
            if to_square[1] not in cls.ranks:
                raise ValueError('Neplatný tah - čtvrtý znak může být pouze 1-8')

            from_col = cls.files_to_cols[from_square[0]]
            from_row = cls.ranks_to_rows[from_square[1]]
            to_col = cls.files_to_cols[to_square[0]]
            to_row = cls.ranks_to_rows[to_square[1]]

            if from_square == to_square:
                raise ValueError('Neplatný tah - shodné počáteční a koncové pole')
            return Move((from_row, from_col), (to_row, to_col), board)
        else:
            pass


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
        return f'{self.symbol}' if self.color == WHITE else f'.{self.symbol}.'

    @abstractmethod
    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        pass

    '''
     metoda pro generovani tahu po diagonalach, je dana takto obecne, aby mohla byt pouzita na generovani tahu strelce 
     a damy
    '''

    @staticmethod
    def generate_pseudo_legal_diagonal_moves(r: int, c: int, game: ChessGame) -> List[Move]:
        moves = []
        piece_pinned = False
        pin_direction = ()
        for i in range(len(game.pins) - 1, -1, -1):
            if game.pins[i][0] == r and game.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (game.pins[i][2], game.pins[i][3])
                # damu chceme z pinu odstranit az ve chvili, kdy generujeme ortogonalni tahy
                if game.board[r][c].piece_type != QUEEN:
                    game.pins.remove(game.pins[i])
                break
        directions = ((-1, 1), (1, -1), (1, 1), (-1, -1))
        enemy_color = BLACK if game.white_to_move else WHITE
        for direction in directions:
            for i in range(1, 8):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # kontrola, ze jsme na sachovnici
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[0]):
                        end_piece = game.board[end_row][end_col]
                        if end_piece is None:
                            moves.append(Move((r, c), (end_row, end_col), game.board))
                        elif end_piece.color == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), game.board))
                            break
                        else:
                            # spratelena figura
                            break
        return moves

    '''
    metoda pro generovani tahu po primkach, je dana takto obecne, aby mohla byt pouzita na generovani tahu veze a damy
    '''

    @staticmethod
    def generate_pseudo_legal_orthogonal_moves(r: int, c: int, game: ChessGame) -> List[Move]:
        moves = []
        piece_pinned = False
        pin_direction = ()
        for i in range(len(game.pins) - 1, -1, -1):
            if game.pins[i][0] == r and game.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (game.pins[i][2], game.pins[i][3])
                game.pins.remove(game.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = BLACK if game.white_to_move else WHITE
        for direction in directions:
            for i in range(1, 8):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # kontrola, ze jsme na sachovnici
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[0]):
                        end_piece = game.board[end_row][end_col]
                        if end_piece is None:
                            moves.append(Move((r, c), (end_row, end_col), game.board))
                        elif end_piece.color == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), game.board))
                            break
                        else:
                            # spratelena figura
                            break
        return moves


class Pawn(Piece):
    piece_type = PieceType.PAWN
    symbol = 'p'

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        moves: List[Move] = []
        piece_pinned = False
        pin_direction = ()
        for i in range(len(game.pins) - 1, -1, -1):
            if game.pins[i][0] == r and game.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (game.pins[i][2], game.pins[i][3])
                game.pins.remove(game.pins[i])
                break

        if self.color == WHITE:
            # kontrola, zda je mozny posun o jedno pole dopredu
            if game.board[r - 1][c] is None:
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), game.board))
                    # kontrola, zda je mozny posun o dve pole dopredu
                    if r == 6 and game.board[r - 2][c] is None:
                        moves.append(Move((r, c), (r - 2, c), game.board))
            if c < 7:  # brani doprava
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r - 1][c + 1] is not None and game.board[r - 1][c + 1].color == BLACK:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), game.board))
                elif len(game.enpassant_square_list) > 0 and (r - 1, c + 1) == game.enpassant_square_list[-1]:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), game.board, is_enpassant_move=True))
            if c > 0:  # brani doleva
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r - 1][c - 1] is not None and game.board[r - 1][c - 1].color == BLACK:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), game.board))
                elif len(game.enpassant_square_list) > 0 and (r - 1, c - 1) == game.enpassant_square_list[-1]:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), game.board, is_enpassant_move=True))
        else:
            # kontrola, zda je mozny posun o jedno pole dopredu
            if game.board[r + 1][c] is None:
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), game.board))
                    # kontrola, zda je mozny posun o dve pole dopredu
                    if r == 1 and game.board[r + 2][c] is None:
                        moves.append(Move((r, c), (r + 2, c), game.board))
            if c < 7:  # brani doprava
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r + 1][c + 1] is not None and game.board[r + 1][c + 1].color == WHITE:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), game.board))
                elif len(game.enpassant_square_list) > 0 and (r + 1, c + 1) == game.enpassant_square_list[-1]:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), game.board, is_enpassant_move=True))
            if c > 0:  # brani doleva
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r + 1][c - 1] is not None and game.board[r + 1][c - 1].color == WHITE:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), game.board))
                elif len(game.enpassant_square_list) > 0 and (r + 1, c - 1) == game.enpassant_square_list[-1]:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), game.board, is_enpassant_move=True))
        return moves


class Rook(Piece):
    piece_type = PieceType.ROOK
    symbol = 'R'

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_orthogonal_moves(r, c, game) or [])

        return moves


class Knight(Piece):
    piece_type = PieceType.KNIGHT
    symbol = 'N'

    '''
    Generuje vsechny kandidaty na tahy pro jezdce. Zde musime prozkoumat vsech 8 moznych poli, kam muze jezdec tahnout
    '''

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        moves: List[Move] = []
        piece_pinned = False
        for i in range(len(game.pins) - 1, -1, -1):
            if game.pins[i][0] == r and game.pins[i][1] == c:
                piece_pinned = True
                game.pins.remove(game.pins[i])
                break
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = WHITE if game.white_to_move else BLACK
        for direction in directions:
            end_row = r + direction[0]
            end_col = c + direction[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = game.board[end_row][end_col]
                    if end_piece is None:
                        moves.append(Move((r, c), (end_row, end_col), game.board))
                    elif end_piece.color != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), game.board))
        return moves


class Bishop(Piece):
    piece_type = PieceType.BISHOP
    symbol = 'B'

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, game) or [])

        return moves


class Queen(Piece):
    piece_type = PieceType.QUEEN
    symbol = 'Q'

    '''
    Generuje vsechny kandidaty na tahy pro damu. Je to kombinace tahu, ktere muze delat vez a strelec, tedy rovne
    tahy a diagonalni tahy
    '''

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, game) or [])
        moves.extend(Piece.generate_pseudo_legal_orthogonal_moves(r, c, game) or [])

        return moves


class King(Piece):
    piece_type = PieceType.KING
    symbol = 'K'

    '''
    Generuje vsechny kandidaty na tahy pro krale. Zde musime prozkoumat vsech 8 moznych poli, kam muze kral tahnout
    '''

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        moves: List[Move] = []
        directions = ((-1, -1), (-1, 0), (-1, 1), (1, 0), (1, 1), (1, -1), (0, -1), (0, 1))
        ally_color = WHITE if game.white_to_move else BLACK
        for direction in directions:
            end_row = r + direction[0]
            end_col = c + direction[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = game.board[end_row][end_col]
                if end_piece is None or end_piece.color != ally_color:
                    if ally_color == WHITE:
                        game.white_king_position = (end_row, end_col)
                    else:
                        game.black_king_position = (end_row, end_col)
                    in_check, pins, checks = game.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), game.board))
                    # vracime krale na puvodni pole
                    if ally_color == WHITE:
                        game.white_king_position = (r, c)
                    else:
                        game.black_king_position = (r, c)
        return moves


class ChessGame:
    def __init__(self) -> None:
        self.board: List[List[Union[Piece, None]]] = [
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
        self.white_king_position: Tuple[int, int] = (7, 4)
        self.black_king_position: Tuple[int, int] = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.game_result: Union[GameResult, None] = None
        # list souradnic poli, kde bylo mozne brat mimochodem - je potreba udrzovat list jako vyvoj tohoto
        # pole kvuli vraceni tahu, abychom mohli obnovovat spravne pole pro brani mimochodem
        self.enpassant_square_list: List[Tuple] = []

    '''
    Metoda provadi tah. Uvolni puvodni pole a na cilove pole umisti figuru, ktera tahne. Tah se ulozi do seznamu tahu.
    Pote se prehodi hrac, ktery je na tahu.
    '''

    def do_move(self, move: Move) -> None:
        self.board[move.start_row][move.start_col] = None
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_stack.append(move)  # ulozime si tah, abychom ho pozdeji mohli vratit
        self.change_turn()
        if move.piece_moved.piece_type == KING and move.piece_moved.color == WHITE:
            self.white_king_position = (move.end_row, move.end_col)
        elif move.piece_moved.piece_type == KING and move.piece_moved.color == BLACK:
            self.black_king_position = (move.end_row, move.end_col)
        # promena pesce
        if move.is_pawn_promotion:
            new_piece = create_piece(move.piece_moved.color, move.promotion_type)
            self.board[move.end_row][move.end_col] = new_piece

        # brani mimochodem
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = None

        # enpassant_square update
        # jestlize mame tah pescem a o 2 pole, tak je jedno pole jako kandidat pro brani mimochodem
        if move.piece_moved.piece_type == PAWN and abs(move.start_row - move.end_row) == 2:
            self.enpassant_square_list.append(((move.start_row + move.end_row) // 2, move.end_col))
        else:
            self.enpassant_square_list.append(())  # resetujeme enpassant pole

    '''
    Metoda vraci tah. Tah si vezme ze seznamu tahu, vyhozenou figuru (pokud nejaka je) vrati zpatky a figuru, 
    ktera tahla vrati na puvodni pole. Dale prehodi hrace, ktery je na tahu.
    '''

    def undo_move(self) -> None:
        if len(self.move_stack) == 0:
            pass
        move = self.move_stack.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.change_turn()
        if move.piece_moved.piece_type == KING and move.piece_moved.color == WHITE:
            self.white_king_position = (move.start_row, move.start_col)
        elif move.piece_moved.piece_type == KING and move.piece_moved.color == BLACK:
            self.black_king_position = (move.start_row, move.start_col)
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_col] = None
            self.board[move.start_row][move.end_col] = move.piece_captured
        # musime znovu nastavit stejne enpassant pole jako bylo pred tahem
        self.enpassant_square_list.pop()

        self.game_result = None

    def change_turn(self):
        self.white_to_move = not self.white_to_move

    '''
    Metoda si nejdrive zjisti vsechny pseudo-legalni tahy volanim metody get_pseudo_legal_moves a pote kontroluje kazdy
    z nich tak, ze si vygeneruje vsechny mozne odpovedi soupere a zjisti, jestli by souper mohl nekterym tahem sebrat 
    krale a pokud ano, takovy tah vylouci. Pote vrati uz pouze seznam legalnich tahu
    '''

    def generate_legal_moves(self) -> List[Move]:
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_position[0]
            king_col = self.white_king_position[1]
        else:
            king_row = self.black_king_position[0]
            king_col = self.black_king_position[1]
        if self.in_check:
            # pouze jeden sach, muzeme blokovat (u dvojsachu nelze)
            if len(self.checks) == 1:
                moves = self.generate_pseudo_legal_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                # policka, kam se figura muze pohnout
                valid_squares = []
                # jestli sachuje jezdec, musime bud jezdce vzit nebo uhnout kralem
                if piece_checking.piece_type == KNIGHT:
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        # check[2] a check[3] jsou smery sachu
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                # prochazime list pozpatku, abychom mohli bez obav mazat
                for i in range(len(moves) - 1, -1, -1):
                    # pokud tah neni kralem, musi to byt block nebo capture
                    if moves[i].piece_moved.piece_type != KING:
                        # jestli tah neblokuje nebo nebere, vyhazujeme ho z listu
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:
                # dvojity sach, pouze tahy krale jsou povoleny
                moves = self.generate_pseudo_legal_moves()
                # prochazime list pozpatku, abychom mohli bez obav mazat
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved.piece_type != KING:
                        moves.remove(moves[i])
        else:
            moves = self.generate_pseudo_legal_moves()

        return moves

    '''
    Metoda zjistuje, jestli je hrac na tahu v sachu, list pinu a list policek, ze kterych je sachovano
    '''

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            enemy_color = BLACK
            ally_color = WHITE
            start_row = self.white_king_position[0]
            start_col = self.white_king_position[1]
        else:
            enemy_color = WHITE
            ally_color = BLACK
            start_row = self.black_king_position[0]
            start_col = self.black_king_position[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            d = directions[i]
            possible_pin = ()
            for j in range(1, 8):
                end_row = start_row + d[0] * j
                end_col = start_col + d[1] * j
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    # posledni cast podminky je kvuli tomu, kdyz generujeme tahy krale, tak docasne kralem pohneme
                    # a zkoumame, jestli neni v sachu, ale vede to k tomu, ze realna figura krale (nepohnuta) by
                    # mohla poskytovat ochranu imaginarnimu krali a vytvaret pin
                    if end_piece is not None and end_piece.color == ally_color and end_piece.piece_type != KING:
                        # 1. spratelna figura v ceste -> mozny pin
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        # 2. spratelena figura v ceste -> zadny pin ani sach neni mozny
                        else:
                            break
                    elif end_piece is not None and end_piece.color == enemy_color:
                        piece_type = end_piece.piece_type
                        # 5 moznosti:
                        # 1) kolmy smer a souperova figura je vez
                        # 2) diagonalni smer a souperova figura je strelec
                        # 3) jakykoliv smer a souperova figura je dama
                        # 4) 1 policko diagonalne a souperova figura je pesec
                        # 5) 1 policko jakymkoliv smerem a souperova figura je kral
                        if (0 <= i <= 3 and piece_type == ROOK) or \
                                (4 <= i <= 7 and piece_type == BISHOP) or \
                                (j == 1 and piece_type == PAWN and ((enemy_color == WHITE and 6 <= i <= 7) or
                                                                    (enemy_color == BLACK and 4 <= i <= 5))) or \
                                (piece_type == QUEEN) or \
                                (i == 1 and piece_type == KING):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    # jsme mimo sachovnici
                    break
        # tahy jezdce
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for knight_move in knight_moves:
            end_row = start_row + knight_move[0]
            end_col = start_col + knight_move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece is not None and end_piece.color == enemy_color and end_piece.piece_type == KNIGHT:
                    in_check = True
                    checks.append((end_row, end_col, knight_move[0], knight_move[1]))
        return in_check, pins, checks

    def has_valid_move(self):
        moves = self.generate_legal_moves()
        if len(moves) == 0:
            return False
        return True

    def is_check(self) -> bool:
        if self.white_to_move:
            return self.is_square_attacked(self.white_king_position[0], self.white_king_position[1])
        else:
            return self.is_square_attacked(self.black_king_position[0], self.black_king_position[1])

    def is_square_attacked(self, r: int, c: int) -> bool:
        self.change_turn()
        opponent_moves = self.generate_pseudo_legal_moves()
        self.change_turn()
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    '''
    Metoda generuje vsechny mozne tahy hrace na tahu s tim, ze se nekontroluje, zda by se hrac na tahu nedostal do 
    sachu. Tuto kontrolu provadi az metoda get_legal_moves
    '''

    def generate_pseudo_legal_moves(self) -> List[Move]:
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece is not None:
                    color = piece.color
                    if (color == WHITE and self.white_to_move) or (color == BLACK and not self.white_to_move):
                        moves.extend(piece.generate_pseudo_legal_moves(r, c, self) or [])
        return moves

    def check_end_result(self) -> None:
        if not self.has_valid_move():
            if self.is_check():
                if self.white_to_move:
                    self.game_result = GameResult.BLACK_WIN
                else:
                    self.game_result = GameResult.WHITE_WIN
            else:
                self.game_result = GameResult.STALEMATE
        if self.is_insufficient_material():
            self.game_result = GameResult.INSUFFICIENT_MATERIAL_DRAW

    def get_result_string(self) -> Union[str, None]:
        if self.game_result == GameResult.WHITE_WIN:
            return '1:0'
        elif self.game_result == GameResult.BLACK_WIN:
            return '0:1'
        elif self.game_result in {GameResult.STALEMATE, GameResult.FIFTY_MOVE_RULE_DRAW,
                                  GameResult.THREEFOLD_REPETITION_DRAW,
                                  GameResult.INSUFFICIENT_MATERIAL_DRAW}:
            return '0,5:0,5'
        else:
            return None

    def is_insufficient_material(self):
        # TODO: dodelat
        return False

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
        for rank in range(len(self.board)):
            self.print_rank(rank)
        print('  |-----|-----|-----|-----|-----|-----|-----|-----|')
        print('     A     B     C     D     E     F     G     H   ')

    def print_info_message(self):
        if self.game_result == GameResult.WHITE_WIN or self.game_result == GameResult.BLACK_WIN:
            print(f'{bcolors.PASS}Checkmate. GameResult: {self.get_result_string()}{bcolors.ENDC}')
        elif self.game_result == GameResult.STALEMATE:
            print(f'{bcolors.PASS}Stalemate. GameResult: {self.get_result_string()}{bcolors.ENDC}')
        elif self.is_check():
            print(f'{bcolors.WARN}Check!{bcolors.ENDC}')
