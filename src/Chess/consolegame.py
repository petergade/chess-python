import bcolors
import time
from rules import ChessGame, Move, GameResult, WHITE, BLACK


class ConsoleGame:

    def __init__(self):
        self.chess_game = ChessGame()

    def print_all_moves(self) -> None:
        """
        Metoda vypise zaznam partie v SAN notaci
        """
        result = ''
        move_index = 1
        for half_move_index, move in enumerate(self.chess_game.move_stack, start=1):
            if half_move_index % 2 == 0:
                result += f' {move.san} '
            else:
                result += f'{move_index}.{move.san}'
                move_index += 1
        if self.chess_game.game_result is not None:
            if self.chess_game.game_result == GameResult.WHITE_WIN:
                result += '# 1-0'
            elif self.chess_game.game_result == GameResult.BLACK_WIN:
                result = result[:-1]
                result += '# 0-1'
            else:
                result += '0.5-0.5'
        print(result)

    def print_board(self) -> None:
        """
        Metoda vypise stav sachovnice po radcich
        """
        for rank in range(len(self.chess_game.board)):
            self.print_rank(rank)
        print('  |-----|-----|-----|-----|-----|-----|-----|-----|')
        print('     A     B     C     D     E     F     G     H   ')

    def print_rank(self, rank: int) -> None:
        """
        Metoda pro vypsani jednoho radku sachovnice
        :param rank: cislo radku sachovnice
        """
        print('  |-----|-----|-----|-----|-----|-----|-----|-----|')
        self.print_pieces(rank)
        self.print_square_colors(rank)

    def print_pieces(self, rank: int) -> None:
        """
        Metoda vypise figury pro dany radek sachovnice. Bile figury vypise jako warning, takze zlute, cerne figury
        vypise zelene, prijde mi to trochu prehlednejsi
        :param rank: radek sachovnice
        """
        s = '  '
        for file in range(len(self.chess_game.board[rank])):
            piece = self.chess_game.board[rank][file]
            if piece is None:
                s += '|     '
            else:
                if piece.color == WHITE:
                    s += f'|{bcolors.WARN}{str(piece).center(5, " ")}{bcolors.ENDC}'
                else:
                    s += f'|{bcolors.PASS}{str(piece).center(5, " ")}{bcolors.ENDC}'
        s += '|'
        print(s)

    def print_square_colors(self, rank: int) -> None:
        """
        Metoda pro vypsani radku sachovnice, kde oznacujeme barvu pole
        :param rank: index radku sachovnice
        :return:
        """
        s = f'{8 - rank} '
        for file in range(len(self.chess_game.board[rank])):
            color = BLACK if (rank + file) % 2 == 0 else WHITE
            if color == WHITE:
                s += '|    w'
            else:
                s += '|    b'
        s += '|'
        print(s)

    def print_info_message(self, move) -> None:
        """
        Metoda vypise, ktery tah byl zahrany a pripadne, zda vzniknul tahem sach, sach mat nebo pat
        :param move: zahrany tah
        :return:
        """
        print(f'Move {move} played')
        if self.chess_game.game_result == GameResult.WHITE_WIN or self.chess_game.game_result == GameResult.BLACK_WIN:
            print(f'{bcolors.PASS}Checkmate. GameResult: {self.chess_game.get_result_string()}{bcolors.ENDC}')
        elif self.chess_game.game_result == GameResult.STALEMATE:
            print(f'{bcolors.PASS}Stalemate. GameResult: {self.chess_game.get_result_string()}{bcolors.ENDC}')
        elif self.chess_game.in_check:
            print(f'{bcolors.WARN}Check!{bcolors.ENDC}')

    def replay_game(self) -> None:
        """
        Metoda prehraje partii od zacatku po pultazich s prodlevou 1.5 sekundy mezi tahy
        """
        move_stack = self.chess_game.move_stack
        self.chess_game = ChessGame()
        for move in move_stack:
            self.play_move(move.san)
            time.sleep(1.5)

    def play_move(self, move: str) -> None:
        """
        Metoda vezme zapis tahu, zvaliduje ho, zda je to platny tah podle SAN notace, pote si vygeneruje vsechny
        legalni tahy a zkusi, jestli zadany tah je mezi legalnimi tahy, pokud ano, tak ho preda k zahrani. Dale
        se zavola vykresleni aktualniho stavu sachovnice a vypise se, ktery tah byl zahran, pripadne zda vzniknul sach,
        sach mat nebo pat. Pokud neni tah validni (neni podle notace) nebo neni legalni (nelze zahrat podle pravidel),
        tak metoda vyhodi vyjimku.
        :param move: zapis tahu prebrany od hrace z konzole
        """
        try:
            if not Move.validate_san(move):
                raise Exception(f'{move} is not valid move (in Standard Algebraic Notation)')
            moves = self.chess_game.generate_legal_moves()

            for i in range(len(moves)):
                if move == moves[i].san:
                    self.chess_game.do_move(moves[i])
                    self.chess_game.check_end_result()
                    self.print_board()
                    self.print_info_message(move)
                    return
            raise Exception(f'{move} is not legal move')
        except Exception as err:
            print(f'{bcolors.FAIL}{err}{bcolors.ENDC}')

    def replay_sample_game(self) -> None:
        """
        Metoda prehraje jednu z mych partii z chess.com - hlavne pro testovani
        """
        self.chess_game = ChessGame()
        sample_game_moves = ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4', 'Bc5', 'Nc3', 'Nf6', 'h3', 'd6', 'd3',
                             '0-0', 'Qe2', 'Qe7', 'Be3', 'Bxe3', 'Qxe3', 'Be6', 'a3', 'Bxc4', 'dxc4', 'a6',
                             '0-0', 'Nh5', 'Ne2', 'Qe6', 'g4', 'Nf6', 'b3', 'Rae8', 'Ng5', 'Qd7', 'Rad1',
                             'h6', 'Nf3', 'Nxg4', 'hxg4', 'Qxg4', 'Ng3', 'Re6', 'Nh2', 'Qh3', 'Nf5', 'Rg6',
                             'Ng3', 'f5', 'Kh1', 'f4', 'Qd2', 'Nd4', 'Qd3', 'f3', 'c3', 'Qg2']
        for move in sample_game_moves:
            self.play_move(move)
            #time.sleep(0.2)

    def start(self):
        print('Game started')
        self.print_board()
        choice = ''

        while choice != 'q':
            self.display_main_menu()
            choice = input("What would you like to do? ")

            if choice == '1':
                move_uci = input('Enter you move: ')
                self.play_move(move_uci)
            elif choice == '2':
                self.print_all_moves()
            elif choice == '3':
                self.replay_game()
            elif choice == '4':
                legal_moves = self.chess_game.generate_legal_moves()
                print(','.join(str(legal_move) for legal_move in legal_moves))
            elif choice == '5':
                self.chess_game.undo_move()
                self.print_board()
                self.chess_game.check_end_result()
                self.print_info_message()
            elif choice == '6':
                self.replay_sample_game()
            elif choice == 'q':
                print("\nThanks for playing. Bye.")
            else:
                print("\nI didn't understand that choice.\n")

    @staticmethod
    def display_main_menu():
        print('[1] - Play move')
        print('[2] - Display all moves already played')
        print('[3] - Replay the game from the beginning')
        # print('[4] - Print legal moves')
        # print('[5] - Undo move')
        # print('[6] - Load sample game')
        print('[q] - Quit app')


if __name__ == '__main__':
    game = ConsoleGame()
    game.start()
    print('Program finished')
