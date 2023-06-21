import socket
import threading
from board import Board

# region variable
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ip_address = "127.0.0.1"
port = 8081
server.bind((ip_address, port))
server.listen(100)

list_of_clients = []
game = None
turn_lock = threading.Lock()
current_player = 1
game_over = False

closed_sockets = set()
# endregion variable

# region connection function
def client_thread(conn):
    global game, current_player, game_over, player_num, list_of_clients, closed_sockets

    this_player_num = player_num
    connection_closed = False

    while True:
        try:
            message = conn.recv(2048).decode()
            if message:
                if game:
                    if game_over:
                        conn.send("Game over. Please start a new game.".encode())
                        connection_closed = True
                        break

                    if this_player_num == current_player:
                        _, move = message.split(":")
                        process_move(int(move) - 1, this_player_num)

                        winner = game.detectWin()
                        if winner != " ":
                            message_to_send = f"Player {this_player_num} wins!"
                            broadcast(message_to_send)
                            broadcast("Game over")
                            game_over = True
                            connection_closed = True
                            break
                        else:
                            current_player = 2 if current_player == 1 else 1
                    else:
                        conn.send("Wait for your turn...".encode())
                else:
                    conn.send("Waiting for second player...".encode())
        except Exception as e:
            print(e)
            connection_closed = True
            break

    if connection_closed:
        with turn_lock:
            try:
                conn.close()
            except:
                pass

            if conn in list_of_clients:
                list_of_clients.remove(conn)

            if game_over or not list_of_clients:
                game = None
                current_player = 1
                game_over = False
                player_num = 0
                closed_sockets.clear()


def safe_close_socket(sock):
    try:
        sock.setblocking(False)
        sock.recv(1)
    except socket.error as e:
        if e.args[0] in [socket.errno.EWOULDBLOCK, socket.errno.EAGAIN]:
            try:
                sock.close()
            except:
                pass
            return True
    return False


def broadcast(message):
    global list_of_clients
    for client_conn in list_of_clients:
        try:
            client_conn.send(message.encode())
        except:
            client_conn.close()
            list_of_clients.remove(client_conn)

    if "Game over" in message:
        for client_conn in list_of_clients:
            client_conn.close()
        list_of_clients.clear()
# endregion connection function

# region game logic
def process_move(move, player_num):
    global game
    letter = "X" if player_num == 1 else "O"

    if game.checkOpen(move) == 1:
        game.dropLetter(move, letter)

    game_state = serialize_game_state(game)
    broadcast(game_state)


def serialize_game_state(game):
    serialized_board = ""
    for y in range(6):
        for x in range(7):
            serialized_board += game.positions[x][5 - y]
            if x < 6:
                serialized_board += " | "
        serialized_board += "\n"
        if y < 5:
            serialized_board += "--|---|---|---|---|---|--\n"
    serialized_board += " 1   2   3   4   5   6   7 "
    return serialized_board
# endregion game logic


# region main program
player_num = 0
while True:
    conn, addr = server.accept()
    print(addr[0] + ' connected')
    list_of_clients.append(conn)
    player_num += 1

    if player_num == 2:
        game = Board()
        broadcast("Game starts!\n")

    threading.Thread(target=client_thread, args=(conn,)).start()
# endregion main program
