import socket
import threading
import time
from board import Board

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ip_address = "127.0.0.1"
port = 8081
server.bind((ip_address, port))
server.listen(100)

list_of_clients = {}
id_counter = 0

client_groups = {}
group_counter = 0

game_in_groups = {}
current_player_in_groups = {}
game_over_in_groups = {}


def get_client_group(id):
    id = int(id)
    global client_groups
    for group_id, client_ids in client_groups.items():
        if id in client_ids:
            return group_id
    return -1


def assign_group_user(id, connection):
    global client_groups
    global group_counter
    global game_in_groups
    global current_player_in_groups

    message = "Welcome. Make your choice:\n1. Create new game room\n"

    if len(client_groups) > 0:
        message += "2. Join existing game room\n"

    message += "Enter your choice: "
    time.sleep(2)
    connection.send(message.encode())

    data = connection.recv(2048).decode().split(":")[1]

    if data == '1':
        client_groups[group_counter] = []
        client_groups[group_counter].append(id)
        client_group = group_counter
        group_counter += 1
    elif (data == '2') and len(client_groups) > 0:
        groups = set(client_groups.keys())
        group_string = "\n".join([("group: "+str(x)) for x in groups])
        connection.send(("Game room list:\n"+group_string+"\nEnter your choice: ").encode())
        data = connection.recv(2048).decode().split(":")[1]
        if int(data) not in client_groups.keys():
            connection.send("game room not exist\n".encode())
            return -1
        client_groups[int(data)].append(id)
        client_group = int(data)
        game_in_groups[int(data)] = Board()
        current_player_in_groups[int(data)] = 1
    else:
        connection.send("wrong command\n".encode())
        return -1

    connection.send("You are assigned to game room: {}\n>>> ".format(client_group).encode())


def client_thread(conn, addr):
    global id_counter
    global client_groups
    global game_in_groups
    global current_player_in_groups

    conn.send(("Your ID is " + str(id_counter)).encode())
    list_of_clients[id_counter] = conn
    client_id = id_counter
    id_counter += 1
    group_id = -1

    while group_id == -1:
        if get_client_group(client_id) == -1:
            group_id = assign_group_user(client_id, conn)

    player_num = len(client_groups[get_client_group(client_id)])

    while True:
        try:
            message = conn.recv(2048).decode()

            if message:
                sender_id, message_text = message.split(":")

                if len(client_groups[get_client_group(client_id)]) < 2:
                    message = "Wait for second player...\n>>> "
                    conn.send(message.encode())
                else:
                    if current_player_in_groups[get_client_group(client_id)] == player_num:
                        process_move(conn, int(message_text) - 1, player_num, get_client_group(client_id), game_in_groups[get_client_group(client_id)])
                        winner = game_in_groups[get_client_group(client_id)].detectWin()
                        if winner != " ":
                            game_in_groups[get_client_group(client_id)] = Board()
                            message_to_send = f"Client ID {client_id} wins!\nGame restarted\n>>>"
                            broadcast_group(conn, get_client_group(client_id), message_to_send)
                        else:
                            current_player_in_groups[get_client_group(client_id)] = 2 if current_player_in_groups[get_client_group(client_id)] == 1 else 1
                    else:
                        conn.send("Wait for your turn...\n>>> ".encode())
            else:
                remove(conn)
        except:
            continue


def remove(connection):
    for client_id, client_conn in list_of_clients.items():
        if client_conn == connection:
            list_of_clients.pop(client_id)
            break


def process_move(connection, move, player_num, group, game):
    letter = "X" if player_num == 1 else "O"

    if game.checkOpen(move) == 1:
        game.dropLetter(move, letter)

    game_state = serialize_game_state(game)
    broadcast_group(connection, group, game_state)


def broadcast_group(connection, group, message):
    global client_groups
    client_ids = client_groups[group]
    adjust_message = message + "\n>>> "
    for client_id, client_conn in list_of_clients.items():
        if client_id in client_ids:
            try:
                client_conn.send(adjust_message.encode())
            except:
                client_conn.close()
                remove(client_conn)


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


while True:
    conn, addr = server.accept()
    print(addr[0] + ' connected')
    threading.Thread(target=client_thread, args=(conn, addr)).start()

conn.close()
