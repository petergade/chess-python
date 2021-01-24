from __future__ import annotations
from typing import Tuple, List, Union
from abc import ABC, abstractmethod
import enum
import re


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


def create_piece(color: Color, piece_type: PieceType) -> Union[BISHOP, KNIGHT, ROOK, QUEEN]:
    """
    Funkce vyuzivana pri promene pesce na jinou figuru.
    :param color: barva figury
    :param piece_type: typ figury
    """
    return {
        BISHOP: Bishop(color),
        KNIGHT: Knight(color),
        ROOK: Rook(color),
        QUEEN: Queen(color)
    }[piece_type]


def get_promotion_piece_type(promotion_type_str: str) -> PieceType:
    """
    Funkce bere jako vstup typ promeny pesce zadane hracem a vraci typ figury.
    :param promotion_type_str: typ figury, ve kterou by chtel hrac promenit pesce
    :return: typ figury
    """
    if promotion_type_str == 'Q':
        return QUEEN
    elif promotion_type_str == 'N':
        return KNIGHT
    elif promotion_type_str == 'B':
        return BISHOP
    elif promotion_type_str == 'R':
        return ROOK
    else:
        raise Exception(f'Invalid promotion type: {promotion_type_str}')


def get_promotion_type_str(promotion_type: PieceType) -> str:
    """
    Funkce konvertuje typ figury na jeji symbol.
    :param promotion_type: typ figury
    :return: symbol figury
    """
    if promotion_type == QUEEN:
        return 'Q'
    elif promotion_type == KNIGHT:
        return 'N'
    elif promotion_type == BISHOP:
        return 'B'
    elif promotion_type == ROOK:
        return 'R'
    else:
        raise Exception(f'Invalid promotion type: {promotion_type}')


def get_piece_type_value(piece_type: PieceType) -> int:
    """
    Funkce prevadi typ figury na relativni hodnotu figury (slouzi pro bodove hodnoceni hracu).
    :param piece_type: typ figury
    :return: hodnota figury
    """
    if piece_type == PAWN:
        return 1
    elif piece_type == KNIGHT:
        return 3
    elif piece_type == BISHOP:
        return 3
    elif piece_type == ROOK:
        return 5
    elif piece_type == QUEEN:
        return 9
    else:
        return 0  # krale nechceme pocitat


class GameResult(enum.Enum):
    """
    Enum vsechn moznych vysledku sachove partie. Implementovany jsou zatim prvni tri.
    """
    WHITE_WIN = 0,
    BLACK_WIN = 1,
    STALEMATE = 2,
    THREEFOLD_REPETITION_DRAW = 3,  # zatim neni implementovano
    FIFTY_MOVE_RULE_DRAW = 4,  # zatim neni implementovano
    INSUFFICIENT_MATERIAL_DRAW = 5  # zatim neni implementovano


class CastlingRights:
    """
    Trida slouzi pouze pro udrzovani dat o pravech k obema typum rosady obou hracu.
    """
    def __init__(self, wk: bool, bk: bool, wq: bool, bq: bool):
        self.wk = wk  # wk - white kingside - pravo bileho na kingside rosadu
        self.bk = bk  # bk - black kingside - pravo cerneho na kingside rosadu
        self.wq = wq  # wq - white queenside - pravo bileho na queenside rosadu
        self.bq = bq  # bq - black queenside - pravo cerneho na queenside rosadu

    def __str__(self) -> str:
        return f'wk: {self.wk}, bk: {self.bk}, wq: {self.wq}, bq: {self.bq}'


class Move:
    """
    Trida pro reprezentaci sachoveho tahu. V soucasne dobe implementovana pouze standardni notace (SAN).
    """
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}
    files = files_to_cols.keys()
    ranks = ranks_to_rows.keys()

    def __init__(self, from_square: Tuple[int, int], to_square: Tuple[int, int], board: List[List[Piece]],
                 promotion_type: PieceType = QUEEN, is_enpassant: bool = False, is_castle: bool = False) -> None:
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
        self.is_enpassant: bool = is_enpassant
        if self.is_enpassant:
            if self.piece_moved.color == WHITE:
                self.piece_captured = board[self.end_row + 1][self.end_col]
            else:
                self.piece_captured = board[self.end_row - 1][self.end_col]
        # rosada
        self.is_castle = is_castle
        # notace tahu - priradime pozdeji, potrebujeme k tomu znat vsechny mozne tahy daneho pultahu kvuli
        # nejednoznacnym tahum
        self.san = None

    def __eq__(self, other: Move) -> bool:
        """
        Metoda porovnava dva tahy podle jejich hash hodnoty.
        :param other: Tah, se kterym srovnavame
        :return: True/False zda jsou tahy stejne
        """
        if isinstance(other, Move):
            return hash(self) == hash(other)
        return False

    def __hash__(self) -> int:
        """
        Metoda pocita hodnotu tahu pro porovnavani tahu, zda jsou stejne.
        :return: hodnota tahu pro porovnavani (hashovani)
        """
        promotion_type_value = 0

        if self.promotion_type == QUEEN:
            promotion_type_value = 1
        elif self.promotion_type == ROOK:
            promotion_type_value = 2
        elif self.promotion_type == KNIGHT:
            promotion_type_value = 3
        elif self.promotion_type == BISHOP:
            promotion_type_value = 4
        # pro porovnavani tahu
        return self.start_row * 10000 + self.start_col * 1000 + self.end_row * 100 + self.end_col * 10 + promotion_type_value

    def __str__(self) -> str:
        """
        Metoda vraci textovou reprezentaci tahu pomoci SAN notace.
        :return: Textova reprezentace tahu pomoci SAN notace
        """
        return self.san

    def __repr__(self) -> str:
        """
        Metoda vraci textovou reprezentaci tahu pomoci SAN notace.
        :return: Textova reprezentace tahu pomoci SAN notace
        """
        return self.san

    @classmethod
    def validate_san(cls, san: str) -> bool:
        """
        Metoda validuje rucni vstup, zda je tahem podle sachove notace.
        :param san: zapis tahu od hrace
        :return: True/False, zda je tah podle sachove notace
        """
        regex = re.compile(r'''
        (
            0-0(?:-0)?  # rosady
            |[NBRQK][a-h]?[1-8]?[a-h][1-8]  # tahy figurami, ktere nic neberou
            |[NBRQK][a-h]?[1-8]?x[a-h][1-8] # tahy figurami, ktere neco berou
            |[a-h][1-8][NBRQ]? # tah pescem s moznym typem promeny
            |[a-h]x[a-h][1-8][\se.p.]?[NBRQ]? # brani pesce s moznym en passant oznacenim a moznym typem promeny
        )
        ''', re.DOTALL | re.VERBOSE)

        match = regex.match(san)
        return match is not None

    @classmethod
    def annotate_moves_san(cls, moves: List[Move]) -> None:
        """
        Metoda vyplnuje SAN (Standard Algebraic Notation) ke kazdemu tahu, ktery dostane na vstupu. Nemuzeme
        delat pro jednotlive tahy, protoze potrebujeme znat vsechny tahy z daneho pultahu kvuli moznym nejednoznacnym
        tahum (kdy mohou dve figury skocit na stejne pole).
        :param moves: Tahy k anotaci (vsechny legalni tahy daneho pultahu)
        """
        for move in moves:
            start_file = cls.cols_to_files[move.start_col]
            end_file = cls.cols_to_files[move.end_col]
            end_rank = cls.rows_to_ranks[move.end_row]
            if move.is_castle:
                if move.start_col < move.end_col:
                    move.san = '0-0'
                else:
                    move.san = '0-0-0'
            elif move.is_enpassant:
                start_file = cls.cols_to_files[move.start_col]
                end_file = cls.cols_to_files[move.end_col]
                end_rank = cls.rows_to_ranks[move.end_row]
                move.san = f'{start_file}x{end_file}{end_rank} e.p.'
            elif move.is_pawn_promotion:
                promotion_type = get_promotion_type_str(move.promotion_type)
                if move.piece_captured is None:
                    move.san = f'{end_file}{end_rank}{promotion_type}'
                else:
                    move.san = f'{start_file}x{end_file}{end_rank}{promotion_type}'
            else:  # ostatni (bezne) tahy
                piece_type = move.piece_moved.symbol if move.piece_moved.piece_type != PAWN else ''
                ambiguous_piece_identification = cls.get_ambiguous_piece_identification(move, moves)
                if move.piece_captured is None:
                    move.san = f'{piece_type}{ambiguous_piece_identification}{end_file}{end_rank}'
                else:
                    if move.piece_moved.piece_type == PAWN:
                        move.san = f'{start_file}x{end_file}{end_rank}'
                    else:
                        move.san = f'{piece_type}{ambiguous_piece_identification}x{end_file}{end_rank}'

    @classmethod
    def get_ambiguous_piece_identification(cls, move: Move, moves: List[Move]) -> str:
        """
        Metoda zkouma tah, jestli je jednoznacny, to znamena, jestli nemuze vice figur skocit na stejne pole
        a v pripade, ze tah vyhodnoti jako nejednoznacny, tak se snazi najit spravnou identifikaci figury.
        :param move: Tah, ktery zkoumame
        :param moves: Vsechny tahy v danem pultahu
        :return: Identifikace figury, tj. sloupec nebo radek napr. "a" nebo "3"
        """
        if move.piece_moved.piece_type != KNIGHT and move.piece_moved.piece_type != ROOK:
            # nejezdnoznacne mohou byt pouze tahy jezdcem nebo vezi
            return ''
        else:
            for m in filter(lambda x: x.end_row == move.end_row and x.end_col == move.end_col and
                                      x.piece_moved.piece_type == move.piece_moved.piece_type, moves):
                if move != m:
                    if m.start_col == move.start_col:
                        return cls.rows_to_ranks[move.start_row]
                    else:
                        return cls.cols_to_files[move.start_col]
            return ''


class Piece(ABC):
    """
    Abstraktni trida figury, z niz dedi jednotlive figury (pesec, jezdec, strelec, vez, dama, kral).
    """
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
        """
        Metoda vraci symbol figury.
        :return: symbol figury
        """
        return f'{self.symbol}' if self.color == WHITE else f'.{self.symbol}.'

    # abstraktni metoda pro generovani pseudo-legalnich tahu, musi vyplnit potomci
    @abstractmethod
    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        """
        Abstraktni metoda pro generovani pseudo-legalnich tahu, musi vyplnit potomci.
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
        pass

    @staticmethod
    def generate_pseudo_legal_diagonal_moves(r: int, c: int, game: ChessGame) -> List[Move]:
        """
        Metoda vraci vsechny pseudo-legalni tahy po diagonalach a pouziva se pro generovani tahu strelce a damy
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
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

    @staticmethod
    def generate_pseudo_legal_orthogonal_moves(r: int, c: int, game: ChessGame) -> List[Move]:
        """
        Metoda vraci vsechny pseudo-legalni tahy po primkach a pouziva se pro generovani tahu veze a damy
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
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
        """
        Metoda generuje vsechny pseudo-legalni tahy pesce. Zde zkoumame moznost posunu o jedno nebo dve pole dopredu,
        brani doprava a doleva, brani mimochodem i promenu pesce
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
        moves: List[Move] = []
        piece_pinned = False
        pin_direction = ()
        # nejprve projdeme vsechny piny a zjistime, zda je nas pesec v pinu
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
                    self.append_moves(r, c, r - 1, c, game, moves)
                    # kontrola, zda je mozny posun o dve pole dopredu
                    if r == 6 and game.board[r - 2][c] is None:
                        self.append_moves(r, c, r - 2, c, game, moves)
            if c < 7:  # brani doprava
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r - 1][c + 1] is not None and game.board[r - 1][c + 1].color == BLACK:
                    if not piece_pinned or pin_direction == (-1, 1):
                        self.append_moves(r, c, r - 1, c + 1, game, moves)
                elif len(game.enpassant_square_log) > 0 and (r - 1, c + 1) == game.enpassant_square_log[-1]:
                    if not piece_pinned or pin_direction == (-1, 1):
                        self.append_moves(r, c, r - 1, c + 1, game, moves)
            if c > 0:  # brani doleva
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r - 1][c - 1] is not None and game.board[r - 1][c - 1].color == BLACK:
                    if not piece_pinned or pin_direction == (-1, -1):
                        self.append_moves(r, c, r - 1, c - 1, game, moves)
                elif len(game.enpassant_square_log) > 0 and (r - 1, c - 1) == game.enpassant_square_log[-1]:
                    if not piece_pinned or pin_direction == (-1, -1):
                        self.append_moves(r, c, r - 1, c - 1, game, moves)
        else:
            # kontrola, zda je mozny posun o jedno pole dopredu
            if game.board[r + 1][c] is None:
                if not piece_pinned or pin_direction == (1, 0):
                    self.append_moves(r, c, r + 1, c, game, moves)
                    # kontrola, zda je mozny posun o dve pole dopredu
                    if r == 1 and game.board[r + 2][c] is None:
                        self.append_moves(r, c, r + 2, c, game, moves)
            if c < 7:  # brani doprava
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r + 1][c + 1] is not None and game.board[r + 1][c + 1].color == WHITE:
                    if not piece_pinned or pin_direction == (1, 1):
                        self.append_moves(r, c, r + 1, c + 1, game, moves)
                elif len(game.enpassant_square_log) > 0 and (r + 1, c + 1) == game.enpassant_square_log[-1]:
                    if not piece_pinned or pin_direction == (1, 1):
                        self.append_moves(r, c, r + 1, c + 1, game, moves, is_enpassant=True)
            if c > 0:  # brani doleva
                # kontrola, jestli na policku, kde chceme brat je souperova figura
                if game.board[r + 1][c - 1] is not None and game.board[r + 1][c - 1].color == WHITE:
                    if not piece_pinned or pin_direction == (1, -1):
                        self.append_moves(r, c, r + 1, c - 1, game, moves)
                elif len(game.enpassant_square_log) > 0 and (r + 1, c - 1) == game.enpassant_square_log[-1]:
                    if not piece_pinned or pin_direction == (1, -1):
                        self.append_moves(r, c, r + 1, c - 1, game, moves, is_enpassant=True)
        return moves

    @staticmethod
    def append_moves(start_row: int, start_col: int, end_row: int, end_col: int, game: ChessGame, moves: List[Move],
                     is_enpassant: bool = False) -> None:
        """
        Metoda je ciste kvuli tomu, abychom mohli pridat vsechny mozne promeny pesce, jinak by slo tahy pridavat
        primo v metode generate_pseudo_legal_moves.
        """
        if (game.white_to_move and end_row > 0) or (not game.white_to_move and end_row < 7):
            moves.append(Move((start_row, start_col), (end_row, end_col), game.board, is_enpassant=is_enpassant))
        else:
            moves.append(Move((start_row, start_col), (end_row, end_col), game.board, promotion_type=QUEEN))
            moves.append(Move((start_row, start_col), (end_row, end_col), game.board, promotion_type=ROOK))
            moves.append(Move((start_row, start_col), (end_row, end_col), game.board, promotion_type=BISHOP))
            moves.append(Move((start_row, start_col), (end_row, end_col), game.board, promotion_type=KNIGHT))


class Rook(Piece):
    piece_type = PieceType.ROOK
    symbol = 'R'

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        """
        Metoda generuje vsechny pseudo-legalni tahy veze. Zde pouze pouzijeme metodu pro generovani tahu po primkach,
        ktera je spolecna pro vez i damu.
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_orthogonal_moves(r, c, game) or [])

        return moves


class Knight(Piece):
    piece_type = PieceType.KNIGHT
    symbol = 'N'

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        """
        Metoda generuje vsechny pseudo-legalni tahy jezdce. Zde musime prozkoumat vsech 8 moznych poli,
        kam muze jezdec tahnout
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
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
        """
        Metoda generuje vsechny pseudo-legalni tahy strelce. Zde pouze pouzijeme metodu pro generovani tahu po diagonalach,
        ktera je spolecna pro strelce i damu
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, game) or [])

        return moves


class Queen(Piece):
    piece_type = PieceType.QUEEN
    symbol = 'Q'

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        """
        Metoda generuje vsechny pseudo-legalni tahy damy. Zde pouzijeme metodu pro generovani tahu po primkach,
        ktera je spolecna pro vez i damu a metodu pro generovani tahu po diagonalach, ktera je spolecne pro strelce a
        damu.
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
        moves: List[Move] = []

        moves.extend(Piece.generate_pseudo_legal_diagonal_moves(r, c, game) or [])
        moves.extend(Piece.generate_pseudo_legal_orthogonal_moves(r, c, game) or [])

        return moves


class King(Piece):
    piece_type = PieceType.KING
    symbol = 'K'

    def generate_pseudo_legal_moves(self, r: int, c: int, game: ChessGame) -> List[Move]:
        """
        Metoda generuje vsechny kandidaty na tahy pro krale. Zde musime prozkoumat vsech 8 moznych poli, kam muze kral
        tahnout. Schvalne nevolame metodu pro tahy rosady, protoze se tim dostavame do nekonecne rekurze kvuli volani
        metody is_square_attacked(), ktera generuje vsechny tahy soupere a tedy i rosadu. Tahy rosady pridavame az v
        metode generate_legal_moves(). Zde na rozdil od ostatnich figur neresime piny.
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :param game: objekt partie
        :return: list pseudo-legalnich tahu
        """
        moves: List[Move] = []
        directions = ((-1, -1), (-1, 0), (-1, 1), (1, 0), (1, 1), (1, -1), (0, -1), (0, 1))
        ally_color = WHITE if game.white_to_move else BLACK
        for direction in directions:
            end_row = r + direction[0]
            end_col = c + direction[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = game.board[end_row][end_col]
                if end_piece is None or end_piece.color != ally_color:
                    # zkusime krale posunout na cilove pole
                    if ally_color == WHITE:
                        game.white_king_position = (end_row, end_col)
                    else:
                        game.black_king_position = (end_row, end_col)
                    in_check, pins, checks = game.check_for_pins_and_checks()
                    # pokud neni v sachu, tah muzeme pridat
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), game.board))
                    # vracime krale na puvodni pole
                    if ally_color == WHITE:
                        game.white_king_position = (r, c)
                    else:
                        game.black_king_position = (r, c)

        return moves

    @staticmethod
    def generate_castling_moves(r: int, c: int, game: ChessGame) -> List[Move]:
        moves = []
        if game.in_check:
            return moves
        # kingside rosada - dve pole napravo od krale musi byt na sachovnici, musi byt prazdna a nesmi na ne
        # utocit zadna souperova figura
        if 0 <= c + 2 < 8 and game.board[r][c + 1] is None and game.board[r][c + 2] is None and \
                not game.is_square_attacked(r, c + 1) and not game.is_square_attacked(r, c + 2):
            if (game.white_to_move and game.castling_rights_log[-1].wk) or \
                    (not game.white_to_move and game.castling_rights_log[-1].bk):
                moves.append(Move((r, c), (r, c + 2), game.board, is_castle=True))
        # queenside rosada - tri pole nalevo od krale musi byt na sachovnici, musi byt prazdna a na prvni dve nesmi
        # utocit zadna souperova figura
        if 0 <= c - 3 < 8 and game.board[r][c - 1] is None and game.board[r][c - 2] is None and game.board[r][
            c - 3] is None and \
                not game.is_square_attacked(r, c - 1) and not game.is_square_attacked(r, c - 2):
            if (game.white_to_move and game.castling_rights_log[-1].wq) or \
                    (not game.white_to_move and game.castling_rights_log[-1].bq):
                moves.append(Move((r, c), (r, c - 2), game.board, is_castle=True))

        return moves


class ChessGame:
    """
    Trida pro sachovou partii.
    """
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
        self.pins: List[Tuple[int, int]] = []
        self.checks: List[Tuple[int, int]] = []
        self.game_result: Union[GameResult, None] = None
        # list souradnic poli, kde bylo mozne brat mimochodem - je potreba udrzovat list jako vyvoj tohoto
        # pole kvuli vraceni tahu, abychom mohli obnovovat spravne pole pro brani mimochodem
        self.enpassant_square_log: List[Tuple] = []
        # log prav pro rosady, kvuli vraceni tahu musime udrzovat
        self.castling_rights_log: List[CastlingRights] = [CastlingRights(True, True, True, True)]

    def do_move(self, move: Move) -> None:
        """
        Metoda provadi tah, ktery ji byl predan na vstupu. Uvolni puvodni pole a na cilove pole umisti figuru,
        ktera tahne. Tah se ulozi do seznamu tahu. Pote se prehodi hrac, ktery je na tahu a updatuje se pozice krale,
        pokud se tahlo kralem. Dale se zkoumaji specialni typy tahu: promena pesce, brani mimochodem a rosada
        :param move: objekt tahu, ktery ma metoda provest
        """
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
        if move.is_enpassant:
            # tady specialne musime odstranit figuru z jineho pole nez kam smeroval tah
            self.board[move.start_row][move.end_col] = None

        # enpassant_square update
        # jestlize mame tah pescem a o 2 pole, tak je jedno pole jako kandidat pro brani mimochodem
        if move.piece_moved.piece_type == PAWN and abs(move.start_row - move.end_row) == 2:
            self.enpassant_square_log.append(((move.start_row + move.end_row) // 2, move.end_col))
        else:
            self.enpassant_square_log.append(())  # resetujeme enpassant pole

        # rosada
        if move.is_castle:
            if move.end_col - move.start_col == 2:  # kingside rosada
                # kral uz je presunuty, takze musime presunout uz pouze vez
                # vime, ze vez skonci vlevo vedle krale a ze byla o jedno pole vpravo od ciloveho pole krale
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                # odstranime vez puvodniho pole
                self.board[move.end_row][move.end_col + 1] = None
            else:  # queenside rosada
                # kral uz je presunuty, takze musime presunout uz pouze vez
                # vime, ze vez skonci vpravo vedle krale a ze byla o dve pole vlevo od ciloveho pole krale
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                # odstranime vez puvodniho pole
                self.board[move.end_row][move.end_col - 2] = None

        # pravo na rosadu
        self.update_castling_rights(move)

    def undo_move(self) -> Union[Move, None]:
        """
        Metoda vraci tah. Tah si vezme ze seznamu tahu, vyhozenou figuru (pokud nejaka je) vrati zpatky a figuru,
        ktera tahla vrati na puvodni pole. Dale prehodi hrace, ktery je na tahu. Pokud byl tah specialni (rosada,
        en passant nebo promena pesce), musime vse dat do puvodniho stavu, k tomu mame napr. log prav na rosadu
        """
        if len(self.move_stack) == 0:
            return None
        move = self.move_stack.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.change_turn()
        if move.piece_moved.piece_type == KING and move.piece_moved.color == WHITE:
            self.white_king_position = (move.start_row, move.start_col)
        elif move.piece_moved.piece_type == KING and move.piece_moved.color == BLACK:
            self.black_king_position = (move.start_row, move.start_col)
        if move.is_enpassant:
            self.board[move.end_row][move.end_col] = None
            self.board[move.start_row][move.end_col] = move.piece_captured
        # musime znovu nastavit stejne enpassant pole jako bylo pred tahem
        self.enpassant_square_log.pop()
        # prava na rosady
        self.castling_rights_log.pop()
        # rosada
        if move.is_castle:
            if move.end_col - move.start_col == 2:  # kingside rosada
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col - 1] = None
            else:  # queenside
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = None
        self.game_result = None

        return move

    def change_turn(self) -> None:
        """
        Metoda prehazuje hrace na tahu.
        """
        self.white_to_move = not self.white_to_move

    def update_castling_rights(self, move: Move) -> None:
        """
        Metoda aktualizuje prava na rosady pro oba hrace
        :param move: tah, ktery provadime
        """
        # nacteme si posledni prava na rosadu
        current_castling_rights = self.castling_rights_log[-1]
        if move.piece_moved.piece_type == KING:
            if move.piece_moved.color == WHITE:
                # upravime pravo na rosadu - jelikoz se pohnul bily kral, tak mazeme obe prava na rosadu pro bileho
                self.castling_rights_log.append(CastlingRights(False, current_castling_rights.bk, False,
                                                               current_castling_rights.bq))
            else:
                # upravime pravo na rosadu - jelikoz se pohnul cerny kral, tak mazeme obe prava na rosadu pro cerneho
                self.castling_rights_log.append(CastlingRights(current_castling_rights.wk, False,
                                                               current_castling_rights.wq, False))
        elif move.piece_moved.piece_type == ROOK:
            # nacteme si posledni prava na rosadu
            current_castling_rights = self.castling_rights_log[-1]
            if move.piece_moved.color == WHITE:
                if move.start_row == 7:
                    if move.start_col == 0:  # leva vez - mazeme pravo bileho na queenside rosadu
                        self.castling_rights_log.append(CastlingRights(current_castling_rights.wk,
                                                                       current_castling_rights.bk,
                                                                       False,
                                                                       current_castling_rights.bq))
                    elif move.start_col == 7:  # prava vez - mazeme pravo bileho na kingside rosadu
                        self.castling_rights_log.append(CastlingRights(False,
                                                                       current_castling_rights.bk,
                                                                       current_castling_rights.wq,
                                                                       current_castling_rights.bq))
            else:
                if move.start_row == 0:
                    if move.start_col == 0:  # leva vez - mazeme pravo cerneho na queenside rosadu
                        self.castling_rights_log.append(CastlingRights(current_castling_rights.wk,
                                                                       current_castling_rights.bk,
                                                                       current_castling_rights.wq,
                                                                       False))
                    elif move.start_col == 7:  # prava vez - mazeme pravo cerneho na kingside rosadu
                        self.castling_rights_log.append(CastlingRights(current_castling_rights.wk,
                                                                       False,
                                                                       current_castling_rights.wq,
                                                                       current_castling_rights.bq))
        else:
            self.castling_rights_log.append(CastlingRights(current_castling_rights.wk,
                                                           current_castling_rights.bk,
                                                           current_castling_rights.wq,
                                                           current_castling_rights.bq))

    def generate_legal_moves(self) -> List[Move]:
        """
        Metoda generuje legalni tahy. Prvni verze teto metody vygenerovala vsechny psude-legalni tahy, pak zkusila kazdy
        tah provest, vygenerovat vsechny mozne tahy soupere a zjistit timto zpusobem, jestli bychom se nedostali tahem
        do sachu. Tento postup byl znacne neefektivni, navic vedl k ruznym rekurzivnim situacim, takze soucasny postup
        je, ze si nejdrive vygenerujeme vsechny pole, odkud je sachovano a vsechna pole, na kterych jsou figury v pinu.
        Nasledne se metoda deli podle toho, zda je hrac na tahu v sachu a je potreba s nim neco delat nebo ne. Metody
        jednotlivych figur pro generovani pseudo-legalnich tahu uz pocitaji s piny, takze neni nutne kontrolovat, zda
        se tahem nedostaneme do sachu.
        :return: list legalnich tahu
        """
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
            if self.white_to_move:
                moves.extend(
                    King.generate_castling_moves(self.white_king_position[0], self.white_king_position[1], self))
            else:
                moves.extend(
                    King.generate_castling_moves(self.black_king_position[0], self.black_king_position[1], self))

        Move.annotate_moves_san(moves)  # anotujeme vsechny legalni tahy daneho pultahu
        return moves

    def check_for_pins_and_checks(self) -> Tuple[bool, List, List]:
        """
        Metoda zjistuje, jestli je hrac na tahu v sachu, dale list poli, na kterych je figura v pinu, tj. nesmi se
        pohnout nebo jen smerem odkud je hrozba, a list policek, ze kterych je sachovano (potrebujeme vedet, jestli
        je pouze jedno nebo jestli jsou dve a jde tim padem o dvojsach)
        :return: Prvni hodnota v tuplu rika, jestli je hrac v sachu, druha hodnota je list pinu a treti je list sachu
        """
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
                                (j == 1 and piece_type == KING):
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

    def has_valid_move(self) -> bool:
        """
        Metoda zjistuje, zda ma hrac alespon jeden legalni tah. Slouzi pro urcovani vysledku partie.
        :return: True/False hodnota, zda ma hrac alespon jeden legalni tah
        """
        moves = self.generate_legal_moves()
        if len(moves) == 0:
            return False
        return True

    def is_square_attacked(self, r: int, c: int) -> bool:
        """
        Metoda zjistuje, zda na dane pole utoci nejaka souperova figura
        :param r: index radku sachovnice
        :param c: index sloupce sachovnice
        :return: True/False, zda na dane utoci souperova figura
        """
        self.change_turn()
        opponent_moves = self.generate_pseudo_legal_moves()
        self.change_turn()
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def generate_pseudo_legal_moves(self) -> List[Move]:
        """
        Metoda generuje vsechny mozne tahy hrace na tahu s tim, ze se nekontroluji vsechna pravidla, resi se pouze piny.
        :return: Seznam pseudo-legalnich tahu, tj. platnych sachovych tahu, ktere ale nemusi byt legalni v dane pozici
        """
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
        """
        Metoda zjistuje a nastavuje vysledek partie.
        """
        if not self.has_valid_move():
            if self.in_check:
                if self.white_to_move:
                    self.game_result = GameResult.BLACK_WIN
                else:
                    self.game_result = GameResult.WHITE_WIN
            else:
                self.game_result = GameResult.STALEMATE
        if self.is_insufficient_material():
            self.game_result = GameResult.INSUFFICIENT_MATERIAL_DRAW

    def get_result_string(self) -> Union[str, None]:
        """
        Metoda prevadi vysledek partie na textovou podobu.
        :return: pokud je vysledek partie znam, vraci se textova reprezentace vysledku, jinak None
        """
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

    def get_naive_position_evaluation(self) -> Tuple[int, int]:
        """
        Metoda spocita pro kazdeho hrace hodnotu jeho figur. (pesec = 1, strelec = jezdec = 3, vez = 5, dama = 9)
        :return: hodnoceni obou hracu
        """
        white_points: int = 0
        black_points: int = 0
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece is not None:
                    if piece.color == WHITE:
                        white_points += get_piece_type_value(piece.piece_type)
                    else:
                        black_points += get_piece_type_value(piece.piece_type)
        return white_points, black_points

    # TODO: dodelat
    def is_insufficient_material(self) -> bool:
        """
        Metoda zjistuje, zda je na sachovnici dostatek materialu pro vyhru jednoho z hracu. Zatim neni implementovano
        :return: True/False hodnota, zda je na sachovnici dostatek materialu pro vyhru jednoho z hracu
        """
        return False
