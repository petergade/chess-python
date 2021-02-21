from typing import List, Tuple, Union
from rules import Move, PieceType, ChessGame, Color, Piece
import random

piece_score = {PieceType.KING: 0, PieceType.QUEEN: 900, PieceType.ROOK: 500, PieceType.BISHOP: 320, PieceType.KNIGHT: 310,
               PieceType.PAWN: 100}
CHECKMATE = 10000
STALEMATE = 0
MAX_DEPTH = 3

pawn_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0]

knights_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]
bishops_table = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]
rooks_table = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0]
queens_table = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]
kings_table = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]


def find_random_move(valid_moves: List[Move]) -> Move:
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_best_move(game: ChessGame, valid_moves: List[Move]) -> Move:
    turn_multiplier = 1 if game.white_to_move else -1
    opponent_min_max_score: int = CHECKMATE
    random.shuffle(valid_moves)
    best_move: Union[Move, None] = None
    for player_move in valid_moves:
        game.do_move(player_move)
        opponent_moves = game.generate_legal_moves()
        if game.game_result is not None and game.game_result.STALEMATE:
            opponent_max_score = STALEMATE
        elif game.game_result is not None and (game.game_result.WHITE_WIN or game.game_result.BLACK_WIN):
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                game.do_move(opponent_move)
                if game.game_result is not None and game.game_result.STALEMATE:
                    score = STALEMATE
                elif game.game_result is not None and (game.game_result.WHITE_WIN or game.game_result.BLACK_WIN):
                    score = CHECKMATE
                else:
                    score = -turn_multiplier * _get_naive_position_evaluation(game)
                if score > opponent_max_score:
                    opponent_max_score = score
                game.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_move = player_move
            print(f'Move: {player_move.san}, score: {opponent_min_max_score}')
        game.undo_move()
    return best_move


def find_best_move_min_max(game: ChessGame, valid_moves: List[Move]) -> Union[Move, None]:
    global best_move
    best_move = None
    find_move_min_max(game, valid_moves, MAX_DEPTH, game.white_to_move)
    return best_move


def find_move_min_max(game: ChessGame, valid_moves: List[Move], depth: int, white_to_move: bool) -> int:
    global best_move
    if depth == 0:
        return _get_naive_position_evaluation(game)

    if white_to_move:
        max_score = -CHECKMATE
        for valid_move in valid_moves:
            game.do_move(valid_move)
            next_moves = game.generate_legal_moves()
            score = find_move_min_max(game, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == MAX_DEPTH:
                    best_move = valid_move
            game.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for valid_move in valid_moves:
            game.do_move(valid_move)
            next_moves = game.generate_legal_moves()
            score = find_move_min_max(game, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == MAX_DEPTH:
                    best_move = valid_move
            game.undo_move()
        return min_score




def _get_naive_position_evaluation(game: ChessGame) -> int:
    """
    Metoda spocita pro kazdeho hrace hodnotu jeho figur.
    :return: hodnoceni obou hracu
    """
    if game.game_result is not None and (game.game_result.WHITE_WIN or game.game_result.BLACK_WIN):
        if game.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif game.game_result is not None and game.game_result.STALEMATE:
        return STALEMATE

    score: int = 0
    for r in range(len(game.board)):
        for c in range(len(game.board[r])):
            piece = game.board[r][c]
            if piece is not None:
                if piece.color == Color.WHITE:
                    score += piece_score[piece.piece_type]
                    score += _get_positional_score(r, c, piece, True)
                else:
                    score -= piece_score[piece.piece_type]
                    score -= _get_positional_score(r, c, piece, False)
    return score


def _get_positional_score(r: int, c: int, piece: Piece, white: bool) -> int:
    square = r * 8 + c if not white else 63 - (r * 8 + c)
    if piece.piece_type == PieceType.PAWN:
        return pawn_table[square]
    elif piece.piece_type == PieceType.KNIGHT:
        return knights_table[square]
    elif piece.piece_type == PieceType.BISHOP:
        return bishops_table[square]
    elif piece.piece_type == PieceType.ROOK:
        return rooks_table[square]
    elif piece.piece_type == PieceType.QUEEN:
        return queens_table[square]
    elif piece.piece_type == PieceType.KING:
        return kings_table[square]

