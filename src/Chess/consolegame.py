from rules import ChessGame, Move


class ConsoleGame:

    def __init__(self):
        self.chess_game = ChessGame()

    # zobrazeni zaznamu partie
    def print_all_moves(self):
        for move, i in self.chess_game.move_stack:
            print('')

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
                print(f'Your move is {move_uci}')
                move = Move.from_uci(move_uci, self.chess_game.board)
                self.chess_game.make_move(move)
                self.chess_game.print_board()
            elif choice == '2':
                print("\nI can't wait to meet this person!\n")
            elif choice == '4':
                legal_moves = self.chess_game.generate_legal_moves()
                print(','.join(str(legal_move) for legal_move in legal_moves))
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
        print('[q] - Quit app')


if __name__ == '__main__':
    game = ConsoleGame()
    game.start()
    print('Program finished')
