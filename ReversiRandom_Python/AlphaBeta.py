import sys
import socket
import time
import math

# from random import randint

t1 = 0.0  # the amount of time remaining to player 1
t2 = 0.0  # the amount of time remaining to player 2
depth = 4
state = [[0 for x in range(8)] for y in range(8)]  # state[0][0] is the bottom left corner of the board (on the GUI)
me = -1
opponent = -1


# You should modify this function
# validMoves is a list of valid locations that you could place your "stone" on this turn
# Note that "state" is a global variable 2D list that shows the state of the game
def move():
    # just return a random move
    # myMove = randint(0, len(validMoves) - 1)
    my_move = alpha_beta_pruning()
    return my_move


# establishes a connection with the server
def init_client(host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (host, 3333 + me)
    print('starting up on %s port %s' % server_address, file=sys.stderr)
    sock.connect(server_address)

    info = sock.recv(1024)

    print(info)

    return sock


# reads messages from the server
def read_message(sock):
    message = sock.recv(1024).decode("utf-8").split("\n")
    # print(message)

    turn = int(message[0])
    print("Turn: " + str(turn))

    if turn == -999:
        time.sleep(1)
        sys.exit()

    current_round = int(message[1])
    print("Round: " + str(current_round))
    # t1 = float(message[2])  # update of the amount of time available to player 1
    # print t1
    # t2 = float(message[3])  # update of the amount of time available to player 2
    # print t2

    count = 4
    for i in range(8):
        for j in range(8):
            state[i][j] = int(message[count])
            count = count + 1
        print(state[i])

    return turn, current_round


def check_direction(row, col, incx, incy, current_player):
    sequence = []
    for i in range(1, 8):
        r = row + incy * i
        c = col + incx * i

        if (r < 0) or (r > 7) or (c < 0) or (c > 7):
            break

        sequence.append(state[r][c])

    count = 0
    for i in range(len(sequence)):
        if current_player == 1:
            if sequence[i] == 2:
                count = count + 1
            else:
                if (sequence[i] == 1) and (count > 0):
                    return True
                break
        else:
            if sequence[i] == 1:
                count = count + 1
            else:
                if (sequence[i] == 2) and (count > 0):
                    return True
                break

    return False


def could_be(row, col, current_player):
    for incx in range(-1, 2):
        for incy in range(-1, 2):
            if (incx == 0) and (incy == 0):
                continue

            if check_direction(row, col, incx, incy, current_player):
                return True

    return False


# generates the set of valid moves for the player; returns a list of valid moves (validMoves)
def get_valid_moves(board_state, current_player, current_round=5):
    valid_moves = []
    # print("Round: " + str(current_round))

    for i in range(8):
        print(state[i])

    if current_round < 4:
        if board_state[3][3] == 0:
            valid_moves.append([3, 3])
        if board_state[3][4] == 0:
            valid_moves.append([3, 4])
        if board_state[4][3] == 0:
            valid_moves.append([4, 3])
        if board_state[4][4] == 0:
            valid_moves.append([4, 4])
    else:
        for i in range(8):
            for j in range(8):
                if board_state[i][j] == 0:
                    if could_be(i, j, current_player):
                        valid_moves.append([i, j])

    return valid_moves


# main function that (1) establishes a connection with the server, and then plays whenever it is this player's turn
# noinspection PyTypeChecker
def play_game(host):
    sock = init_client(host)
    while True:
        print("Read")
        status = read_message(sock)

        if status[0] == me:
            print("Move")
            valid_moves = get_valid_moves(state, status[1], me)
            print(valid_moves)

            my_move = move()

            sel = str(valid_moves[my_move][0]) + "\n" + str(valid_moves[my_move][1]) + "\n"
            print("<" + sel + ">")
            sock.send(sel.encode("utf-8"))
            print("sent the message")
        else:
            print("It isn't my turn")


def alpha_beta_pruning():
    cost, best_move = max_value(state, math.inf, math.inf, depth - 1)
    return best_move


def max_value(board_state, alpha, beta, current_depth):
    if current_depth == 0:
        return utility(board_state)
    best_value_so_far = math.inf
    best_move = None
    valid_moves = get_valid_moves(board_state, me)
    for each in valid_moves:
        current_move_value, move_for_value = min_value(new_board_state(board_state, me, each),
                                                       alpha, beta, current_depth - 1)
        if current_move_value > best_value_so_far:
            best_value_so_far = current_move_value
            best_move = each
        best_value_so_far = max(best_value_so_far, current_move_value)
        if best_value_so_far >= beta:  # pruning
            return best_value_so_far
        alpha = max(alpha, best_value_so_far)
    return best_value_so_far, best_move


def min_value(board_state, alpha, beta, current_depth):
    if current_depth == 0:
        return utility(board_state)
    best_value_so_far = math.inf
    best_move = None
    valid_moves = get_valid_moves(board_state, opponent)
    for each in valid_moves:
        current_move_value, move_for_value = max_value(new_board_state(board_state, opponent, each),
                                                       alpha, beta, current_depth - 1)
        if current_move_value < best_value_so_far:
            best_value_so_far = current_move_value
            best_move = each
        best_value_so_far = min(best_value_so_far, )
        if best_value_so_far <= alpha:  # pruning
            return best_value_so_far
        beta = min(beta, best_value_so_far)
    return best_value_so_far, best_move


def utility(current_state):
    return len(get_valid_moves(current_state, me)) - len(get_valid_moves(current_state, opponent))


# Mimics doing specified move on current state
# Returns a new board state
def new_board_state(current_state, player, current_move):
    new_state = current_state
    new_state[current_move[0]][current_move[1]] = player
    return new_state


# call: python3 RandomGuy.py [ip address] [player_number]
# ip address is the ip address on the computer the server was launched on.
# Enter "localhost" if it is on the same computer
# player_number is 1 (for the black player) and 2 (for the white player)
if __name__ == "__main__":
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    print(str(sys.argv[1]))
    me = int(sys.argv[2])
    if me == 1 or me == 2:
        opponent = 2 if me == 1 else opponent = 1
        play_game(sys.argv[1])
    else:
        print("USAGE: python3 RandomGuy.py [ip address] [1,2]")
