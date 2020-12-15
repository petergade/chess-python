from typing import List
from rules import ChessGame, Move, Piece
import pygame as p

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images() -> None:
    pieces = ['p', 'R', 'N', 'B', 'Q', 'K', '.p.', '.R.', '.N.', '.B.', '.Q.', '.K.']
    for piece in pieces:
        file_name_without_extension = f'w{piece}' if '.' not in piece else f'b{piece.replace(".", "")}'
        IMAGES[piece] = p.image.load(f'images/{file_name_without_extension}.png')


def main() -> None:
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
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
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    game.undo_move()
                    move_made = True
            elif e.type == p.MOUSEBUTTONDOWN:
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
                    move = Move(player_clicks[0], player_clicks[1], game.board)
                    # print(move.get_chess_notation())
                    if move in valid_moves:
                        game.make_move(move)
                        move_made = True
                    sq_selected = ()
                    player_clicks = []
        if move_made:
            valid_moves = game.generate_legal_moves()
            print('Possible moves: ' + ','.join(str(move) for move in valid_moves))
            move_made = False
        draw_game_state(screen, game.board)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen: p.Surface, board: List[List[Piece]]) -> None:
    draw_board(screen)
    draw_pieces(screen, board)


def draw_board(screen: p.Surface) -> None:
    colors = [p.Color("white"), p.Color("grey")]
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


if __name__ == "__main__":
    main()
