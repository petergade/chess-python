from typing import List, Tuple
from rules import ChessGame, Move, Piece, Color
import engine
import pygame as p

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
WHITE = Color.WHITE
BLACK = Color.BLACK


def load_images() -> None:
    pieces = ['p', 'R', 'N', 'B', 'Q', 'K', '.p.', '.R.', '.N.', '.B.', '.Q.', '.K.']
    for piece in pieces:
        file_name_without_extension = f'w{piece}' if '.' not in piece else f'b{piece.replace(".", "")}'
        IMAGES[piece] = p.image.load(f'images/{file_name_without_extension}.png')


def show_result(result: str, screen: p.Surface) -> None:
    font = p.font.Font('freesansbold.ttf', 48)
    green = (0, 255, 0)
    blue = (0, 0, 128)
    text = font.render(result, True, green, blue)
    text_rect = text.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.blit(text, text_rect)


def main() -> None:
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('chess')
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game = ChessGame()
    valid_moves = game.generate_legal_moves()
    print('Possible moves: ' + ','.join(str(move) for move in valid_moves))
    move_made = False
    load_images()
    running = True
    sq_selected = ()
    player_clicks = []
    is_white_human = True
    is_black_human = False
    is_game_over = False
    while running:
        is_human_turn = (game.white_to_move and is_white_human) or (not game.white_to_move and is_black_human)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    is_game_over = False
                    game.undo_move()
                    move_made = True
            elif e.type == p.MOUSEBUTTONDOWN:
                if not is_game_over and is_human_turn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        if game.board[player_clicks[0][0]][player_clicks[0][1]] is not None:
                            move = Move(player_clicks[0], player_clicks[1], game.board)
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:
                                    game.do_move(valid_moves[i])
                                    game.check_end_result()
                                    move_made = True
                                    sq_selected = ()
                                    player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]

        # AI
        if not is_game_over and not is_human_turn:
            best_move = engine.find_best_move_min_max(game, valid_moves)
            if best_move is None:
                best_move = engine.find_random_move(valid_moves)
            game.do_move(best_move)
            game.check_end_result()
            move_made = True

        if move_made:
            valid_moves = game.generate_legal_moves()
            print('Possible moves: ' + ','.join(str(move) for move in valid_moves))
            # print('Pins: ' + ','.join(str(pin) for pin in game.pins))
            # print('En passant square: ' + str(game.enpassant_square_log[-1]) if len(game.enpassant_square_log) > 0 else 'none')
            print('Castling rights: ' + str(game.castling_rights_log[-1]))
            move_made = False
        draw_game_state(screen, game, valid_moves, sq_selected)
        if game.game_result is not None:
            result = game.get_result_string()
            show_result(result, screen)
            is_game_over = True
        clock.tick(MAX_FPS)
        p.display.flip()


def highlight_squares(screen: p.Surface, game: ChessGame, valid_moves: List[Move], sq_selected: Tuple[int, int]) -> None:
    if sq_selected != ():
        r, c = sq_selected
        if game.board[r][c] is not None and (game.board[r][c].color == WHITE if game.white_to_move else BLACK):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def draw_game_state(screen: p.Surface, game: ChessGame, valid_moves: List[Move], sq_selected: Tuple) -> None:
    draw_board(screen)
    highlight_squares(screen, game, valid_moves, sq_selected)
    draw_pieces(screen, game.board)


def draw_board(screen: p.Surface) -> None:
    colors = [p.Color('white'), p.Color('grey')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen: p.Surface, board: List[List[Piece]]) -> None:
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece is not None:
                screen.blit(IMAGES[str(piece)], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == '__main__':
    main()
