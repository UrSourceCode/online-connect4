import socket
import threading
import time
from board import Board
import json
import copy

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

json_data = {
    "game": []
}

json_file_name = "game_data.json"

with open(json_file_name, 'w') as file:
    json.dump(json_data, file)

json_game_template = {
    "room": -1,
    "player": {
        "red_id": -1,
        "yellow_id": -1
    },
    "board": [],
    "winner_id": -1,
    "game_over": False
}

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
    global json_data

    # message = "choice:[1"

    # if len(client_groups) > 0:
    #     message += ",2]"
    # else:
    #     message += "]"

    time.sleep(2)

    data = connection.recv(2048).decode().split(":")[1]

    if data == '1':
        client_groups[group_counter] = []
        client_groups[group_counter].append(id)
        client_group = group_counter
        game_in_groups[group_counter] = Board()
        
        json_data["game"].append(copy.deepcopy(json_game_template))

        json_data["game"][group_counter]["room"] = group_counter
        json_data["game"][group_counter]["player"]["red_id"] = id
        json_data["game"][group_counter]["board"] = game_in_groups[group_counter].getArray()
        
        with open(json_file_name, 'w') as file:
            json.dump(json_data, file)

        broadcast_group(connection, client_group, json_data)

        group_counter += 1


    elif (data == '2') and len(client_groups) > 0:
        groups = set(client_groups.keys())
        group_string = "[" + ",".join([(str(x)) for x in groups]) + "]"
        # connection.send(("room:"+group_string).encode())
        data = connection.recv(2048).decode().split(":")[1]
        if int(data) not in client_groups.keys():
            connection.send("game room not exist\n".encode())
            return -1
        client_groups[int(data)].append(id)
        client_group = int(data)
        current_player_in_groups[int(data)] = 1

        with open(json_file_name, 'r') as file:
            json_data = json.load(file)

        json_data["game"][int(data)]["player"]["yellow_id"] = id

        with open(json_file_name, 'w') as file:
            json.dump(json_data, file)

        broadcast_group(connection, client_group, json_data)

    else:
        connection.send("wrong command\n".encode())
        return -1

    connection.send("You are assigned to game room {}\n".format(client_group).encode())


def client_thread(conn, addr):
    global id_counter
    global client_groups
    global game_in_groups
    global current_player_in_groups
    global json_data

    conn.send(("Your ID is " + str(id_counter)).encode())
    conn.send(json.dumps(json_data).encode())

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

                client_group = get_client_group(client_id)

                if len(client_groups[client_group]) < 2:
                    message = "Wait for second player..."
                    conn.send(message.encode())
                else:
                    if current_player_in_groups[client_group] == player_num:
                        # print("Player {} move: {}".format(player_num, message_text))
                        process_move(conn, int(message_text) - 1, player_num, client_group, game_in_groups[client_group])
                        current_player_in_groups[client_group] = 2 if current_player_in_groups[client_group] == 1 else 1
                    else:
                        conn.send("Wait for your turn...".encode())
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

    # game_state = serialize_game_state(game)
    playingBoard = game.getArray()
    with open(json_file_name, 'r') as file:
        json_data = json.load(file)

    json_data["game"][group]["board"] = playingBoard

    winner = game.detectWin()
    if winner != " ":
        if winner == "X":
            json_data["game"][group]["winner_id"] = json_data["game"][group]["player"]["red_id"]
        else:
            json_data["game"][group]["winner_id"] = json_data["game"][group]["player"]["yellow_id"]
        json_data["game"][group]["game_over"] = True

    with open(json_file_name, 'w') as file:
        json.dump(json_data, file)

    # message_to_send = "board:" + str(playingBoard)
    # print(playingBoard)
    # broadcast_group(connection, group, game_state)
    broadcast_group(connection, group, json_data)


def broadcast_group(connection, group, message):
    global client_groups
    client_ids = client_groups[group]
    # adjust_message = str(message)
    # print("json_data:", message)
    for client_id, client_conn in list_of_clients.items():
        if client_id in client_ids:
            try:
                # client_conn.send(adjust_message.encode())
                client_conn.send(json.dumps(message).encode())
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
