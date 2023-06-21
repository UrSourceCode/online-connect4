import socket
import sys
import threading

# region variable
terminal_width = 50
selected_menu = 0
game_mode = 0
# endregion


# region start screen function
def print_line_of_dashes():
    line_of_dashes = '-' * terminal_width
    print(line_of_dashes)


def print_welcome_message():
    print_line_of_dashes()
    print('WELCOME TO ONLINE CONNECT 4'.center(terminal_width))
    print('version: 0.0.1'.center(terminal_width))
    print('created by Group 2 Network Programming'.center(terminal_width))
    print_line_of_dashes()


def print_main_menu():
    print_line_of_dashes()
    print('Main Menu'.center(terminal_width))
    print_line_of_dashes()
    print('(1) Start Game.')
    print('(2) Exit.')


# endregion


# region choose game screen function
def print_choose_game_mode():
    print_line_of_dashes()
    print('Choose Game Mode'.center(terminal_width))
    print_line_of_dashes()
    print('(1) Single Player (VS Bot).')
    print('(2) Multiplayer (VS Local Player).')
    print('(3) Multiplayer (VS Online Player).')
    print('(4) Exit to main menu.')
    print_line_of_dashes()


# endregion


# region socket
connection_closed = False


def send_msg(sock):
    global connection_closed
    while True:
        move = input("Enter your move (1-7) or 'q' to quit: ")
        if move == 'q':
            sock.send('quit'.encode())
            break
        while not move.isdigit() or not 1 <= int(move) <= 7:
            print("Error: Invalid move. Please enter a number between 1 and 7.")
            move = input("Enter your move (1-7): ")
        message = f"move:{move}"
        sock.send(message.encode())

    connection_closed = True
    sock.close()


def recv_msg(sock):
    global game_mode, connection_closed
    while True:
        if connection_closed:
            break

        data = sock.recv(2048)
        if not data:
            print("Connection closed by the server.")
            sock.close()
            break
        message = data.decode()
        sys.stdout.write("\n" + message + "\n")
        if "Game over" in message:
            connection_closed = True
            sock.close()
            game_mode = 0
# endregion


# region main program
print_welcome_message()

while selected_menu != 1 and selected_menu != 2:
    print_main_menu()
    selected_menu = int(input('Please select menu: '))
    if selected_menu == 1:
        print_choose_game_mode()
        while game_mode != 3:
            game_mode = int(input('Please select game mode: '))
            if game_mode == 3:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip_address = '127.0.0.1'
                port = 8081
                server.connect((ip_address, port))

                threading.Thread(target=send_msg, args=(server,)).start()
                threading.Thread(target=recv_msg, args=(server,)).start()
                break
        break
    elif selected_menu == 2:
        print('exit.')
        sys.exit()
    else:
        print('Error: wrong input (1 / 2), please try again.')
# endregion
