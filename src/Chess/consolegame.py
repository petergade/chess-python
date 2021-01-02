import bcolors as bcolors
from rules import ChessGame, Move


class ConsoleGame:

    def __init__(self):
        self.chess_game = ChessGame()

    # zobrazeni zaznamu partie
    def print_all_moves(self):
        result = ''
        move_index = 1
        for half_move_index, move in enumerate(self.chess_game.move_stack, start=1):
            if half_move_index % 2 == 0:
                result += f' {move.get_uci_chess_notation()} '
            else:
                result += f'{move_index}.{move.get_uci_chess_notation()}'
                move_index += 1
        print(result)

    # prehravani partie po pultazich
    def replay_game(self):
        for move, i in self.chess_game.move_stack:
            print('')

    # navrat do pozice po poslednim tahu
    def go_to_latest_move(self):
        pass

    def start(self):
        print('Game started')
        self.chess_game.print_board()
        choice = ''

        while choice != 'q':
            self.display_main_menu()
            choice = input("What would you like to do? ")

            # Respond to the user's choice.
            if choice == '1':
                move_uci = input('Enter you move: ')
                try:
                    move = Move.from_uci(move_uci, self.chess_game.board)
                    moves = self.chess_game.generate_legal_moves()
                    if move not in moves:
                        raise Exception(f'Move {move_uci} is illegal')
                    self.chess_game.do_move(move)
                    self.chess_game.print_board()
                    self.chess_game.check_end_result()
                    self.chess_game.print_info_message()
                except Exception as err:
                    print(f'{bcolors.FAIL}{err}{bcolors.ENDC}')
            elif choice == '2':
                self.print_all_moves()
            elif choice == '4':
                legal_moves = self.chess_game.generate_legal_moves()
                print(','.join(str(legal_move) for legal_move in legal_moves))
            elif choice == '5':
                self.chess_game.undo_move()
                self.chess_game.print_board()
                self.chess_game.check_end_result()
                self.chess_game.print_info_message()
            elif choice == 'q':
                print("\nThanks for playing. Bye.")
            else:
                print("\nI didn't understand that choice.\n")

    @staticmethod
    def display_main_menu():
        print('[1] - Play move')
        print('[2] - Display all moves already played')
        print('[3] - Replay the game from the beginning')
        print('[4] - Print legal moves')
        print('[5] - Undo move')
        print('[q] - Quit app')


if __name__ == '__main__':
    game = ConsoleGame()
    game.start()
    print('Program finished')
