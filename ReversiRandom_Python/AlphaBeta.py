import sys
import socket
import time
import math
import copy
import random
# from random import randint

t1 = 0.0  # the amount of time remaining to player 1
t2 = 0.0  # the amount of time remaining to player 2
depth = 6
state = [[0 for x in range(8)] for y in range(8)]  # state[0][0] is the bottom left corner of the board (on the GUI)
me = -1
opponent = -1
position_values = [[99,  -8,  8,  6,  6,  8,  -8, 99],
                   [-8, -40, -4, -3, -3, -4, -40, -8],
                   [ 8,  -4,  7,  4,  4,  7,  -4,  8],
                   [ 6,  -3,  4,  0,  0,  4,  -3,  6],
                   [ 6,  -3,  4,  0,  0,  4,  -3,  6],
                   [ 8,  -4,  7,  4,  4,  7,  -4,  8],
                   [-8, -40, -4, -3, -3, -4, -40, -8],
                   [99,  -8,  8,  6,  6,  8,  -8, 99]]

# You should modify this function
# validMoves is a list of valid locations that you could place your "stone" on this turn
# Note that "state" is a global variable 2D list that shows the state of the game
def move(current_round):
    if current_round < 4:
        valid_moves = get_valid_moves(state, me, current_round)
        moveint = random.randint(0, len(valid_moves)-1)
        return valid_moves[moveint]
    move = alpha_beta_pruning(current_round)
    return move

def basic_util(current_state):
    p = 0
    o = 0
    for i in range(8):
        for j in range(8):
            if current_state[i][j] == me:
                p += 1
            elif current_state[i][j] == opponent:
                o += 1
    return (1000 *(p-0))/(p+o+2)


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

def check_direction(board_state, row, col, incx, incy, current_player):
    sequence = []
    for i in range(1, 8):
        r = row + incy * i
        c = col + incx * i

        if (r < 0) or (r > 7) or (c < 0) or (c > 7):
            break

        sequence.append(board_state[r][c])

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

def could_be(board_state, row, col, current_player):
    for incx in range(-1, 2):
        for incy in range(-1, 2):
            if (incx == 0) and (incy == 0):
                continue

            if check_direction(board_state, row, col, incx, incy, current_player):
                return True

    return False

# generates the set of valid moves for the player; returns a list of valid moves (validMoves)
def get_valid_moves(board_state, current_player, current_round):
    valid_moves = []
    # print("Round: " + str(current_round))

    # for i in range(8):
    #     print(state[i])

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
                    if could_be(board_state, i, j, current_player):
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
            current_round = status[1]
            #print(current_round)
            # valid_moves = get_valid_moves(state, status[1], me)
            # print(valid_moves)

            my_move = move(current_round)

            sel = str(my_move[0]) + "\n" + str(my_move[1]) + "\n"
            print("<" + sel + ">")
            sock.send(sel.encode("utf-8"))
            print("sent the message")
        else:
            print("It isn't my turn")

def alpha_beta_pruning(current_round):
    if current_round < 59:
        cost, best_move = max_value(state, -math.inf, math.inf, depth, current_round)
    else:
        cost, best_move = max_value(state, -math.inf, math.inf, 15, current_round)
    return best_move

def board_full(current_state):
    for i in range(8):
        for j in range(8):
            if current_state[i][i] == 0:
                return False
    return True

def max_value(board_state, alpha, beta, current_depth, current_round):
    if current_depth == 0:
        return utility(board_state, current_round), None
    best_value_so_far = -math.inf
    best_move = None
    valid_moves = get_valid_moves(board_state, me, current_round)
    if len(valid_moves) == 0:
        return utility(board_state, current_round), None
    for each in valid_moves:
        current_move_value, move_for_value = min_value(new_board_state(board_state, me, each),
                                                       alpha, beta, current_depth - 1, current_round + 1)
        if current_move_value > best_value_so_far:
            best_value_so_far = current_move_value
            best_move = each
        if best_move is None:
            print("An error has occurred with selecting best move")
        if best_value_so_far >= beta:  # pruning
            return best_value_so_far, best_move
        alpha = max(alpha, best_value_so_far)
    return best_value_so_far, best_move

def min_value(board_state, alpha, beta, current_depth, current_round):
    if current_depth == 0:
        return utility(board_state, current_round), None
    best_value_so_far = math.inf
    best_move = None
    valid_moves = get_valid_moves(board_state, opponent, current_round)
    if len(valid_moves) == 0:
        return utility(board_state, current_round), None
    for each in valid_moves:
        current_move_value, move_for_value = max_value(new_board_state(board_state, opponent, each),
                                                       alpha, beta, current_depth - 1, current_round + 1)
        if current_move_value < best_value_so_far:
            best_value_so_far = current_move_value
            best_move = each
        if best_move is None:
            print("An error has occurred with selecting best move")

        if best_value_so_far <= alpha:  # pruning
            return best_value_so_far, best_move
        beta = min(beta, best_value_so_far)
    return best_value_so_far, best_move

def random_sampling(board_state, current_round):
    best_util = math.inf
    move = None
    for i in range(0, 500):
        valid_moves = get_valid_moves(board_state, me, current_round)
        if len(valid_moves) == 0:
            return revised_utility(board_state, current_round)
        move = random.randint(0, len(valid_moves)-1)
        util = opp_recurse(new_board_state(board_state, me, valid_moves[move]), current_round + 1)
        real_move = valid_moves[move]
        if util > best_util:
            best_util = util
            move = move
    return util, move

def opp_recurse(current_state, current_round):
    valid_moves = get_valid_moves(current_state, opponent, current_round)
    if len(valid_moves) == 0:
        return revised_utility(current_state, current_round)
    move = random.randint(0, len(valid_moves)-1)
    util = me_recurse(new_board_state(current_state, opponent, valid_moves[move]), current_round + 1)
    return util

def me_recurse(current_state, current_round):
    valid_moves = get_valid_moves(current_state, me, current_round)
    if len(valid_moves) == 0:
        return revised_utility(current_state, current_round)
    move = random.randint(0, len(valid_moves)-1)
    util = opp_recurse(new_board_state(current_state, me, valid_moves[move]), current_round + 1)
    return util

def revised_utility(current_state, current_round):
    esac= 312 + (6.24 * current_round)
    cmac = 0
    if current_round <= 25:
        cmac = 50 + (2 * current_round)
    else:
        cmac = 75 + current_round
    edge_stability = get_edge_stability(current_state)
    #internal_stability = get_internal_stability(current_state)
    current_mobility = get_current_mobility(current_state, current_round)
    potential_mobility = get_potential_mobility(current_state)
    return (esac * edge_stability) + (cmac * current_mobility) + (99 * potential_mobility)# + (36 * internal_stability)

def get_edge_stability(current_state):
    stability = 0
    if(current_state[0][0] == me):
        stability += 700
    if(current_state[0][7] == me):
        stability += 700
    if(current_state[7][0] == me):
        stability += 700
    if(current_state[7][7] == me):
        stability += 700
    for i in range(1,7):
        stability += is_stable(current_state, 0, i, me)
        stability += is_stable(current_state, 7, i, me)
        stability += is_stable(current_state, i, 0, me)
        stability += is_stable(current_state, i, 7, me)

    return stability

def get_current_mobility(current_state, current_round):
    p = len(get_valid_moves(current_state, me, current_round))
    o = len(get_valid_moves(current_state, opponent, current_round))
    return ((1000 * (p - o))/(p + o + 2))

def get_potential_mobility(current_state):
    p = get_frontier(current_state, opponent)
    o = get_frontier(current_state, me)
    return ((1000 * (p - o))/(p + o + 2))

def get_frontier(current_state, player):
    total_blanks_next_to_opp_counted_multiple = 0
    total_opp_with_blanks = 0
    total_blanks_next_to_opp = 0
    for i in range(8):
        for j in range(8):
            if current_state[i][j] == player:
                blank_count = 0
                if j < 7:
                    if current_state[i][j+1] == 0:
                        blank_count += 1
                        break
                    if i > 0:
                        if current_state[i-1][j+1] == 0:
                            blank_count += 1
                    if i < 7:
                        if current_state[i+1][j+1] == 0:
                            blank_count += 1
                if j > 0:
                    if current_state[i][j-1] == 0:
                        blank_count += 1
                    if i < 7:
                        if current_state[i+1][j-1] == 0:
                            blank_count += 1
                    if i > 0:
                        if current_state[i-1][j-1] == 0:
                            blank_count += 1
                if i < 7:
                    if current_state[i+1][j] == 0:
                        blank_count += 1
                if i > 0:
                    if current_state[i-1][j] == 0:
                        blank_count += 1
                if blank_count > 0:
                    total_blanks_next_to_opp_counted_multiple += blank_count
                    total_opp_with_blanks += 1
            elif current_state[i][j] == 0:
                if j < 7:
                    if current_state[i][j+1] == player:
                        total_blanks_next_to_opp += 1
                        break
                    if i > 0:
                        if current_state[i-1][j+1] == player:
                            total_blanks_next_to_opp += 1
                            break
                    if i < 7:
                        if current_state[i+1][j+1] == player:
                            total_blanks_next_to_opp += 1
                            break
                if j > 0:
                    if current_state[i][j-1] == player:
                        total_blanks_next_to_opp += 1
                        break
                    if i < 7:
                        if current_state[i+1][j-1] == player:
                            total_blanks_next_to_opp += 1
                            break
                    if i > 0:
                        if current_state[i-1][j-1] == player:
                            total_blanks_next_to_opp += 1
                            break
                if i < 7:
                    if current_state[i+1][j] == player:
                        total_blanks_next_to_opp += 1
                        break
                if i > 0:
                    if current_state[i-1][j] == player:
                        total_blanks_next_to_opp += 1
                        break


    return total_opp_with_blanks + total_blanks_next_to_opp + total_blanks_next_to_opp_counted_multiple

def utility(current_state, current_round):

    ##---- FOR IF WE CAN GET TO THE END OF THE TREE ----##
    if current_round > 59:
        utility = 0
        for i in range(8):
            for j in range(8):
                if current_state[i][j] == me:
                    utility += 1
        return utility

    ##---- FOR FRONTIER STRATEGY ----##
    #good_moves = get_move_utility(current_state, me)
    #bad_moves = get_move_utility(current_state, opponent)
    #return good_moves - bad_moves

    ##---- FOR POSITION VALUE STRATEGY ---##
    my_utility = board_value(current_state, me)
    opp_utility = board_value(current_state, opponent)
    return (my_utility - opp_utility)

##---- FOR POSITION VALUE STRATEGY ----##
def board_value(board_state, current_player):
    total_utility = 0
    for i in range(8):
        for j in range(8):
            if board_state[i][j] == current_player:
                total_utility += position_values[i][j]

    return total_utility

def corner_claimed(board_state):
    return board_state[0][7] != 0 or board_state[7][7] != 0 or board_state[7][0] != 0 or board_state[0][0] != 0

def danger_zones(current_state, player):
    danger_one = True
    danger_two = True
    danger_three = True
    danger_four = True
    danger_five = True
    danger_six = True
    for i in range (1, 7):
        if(current_state[0][i] != player):
            danger_one = False
        if(current_state[7][i] != player):
            danger_two = False
        if(current_state[i][0] != player):
            danger_three = False
        if(current_state[i][7] != player):
            danger_four = False
        if(current_state[i][i] != player):
            danger_five = False
        if(current_state[i][8 - i] != player):
            danger_six = False

    util = 0
    if(danger_one):
        #print("danger_one")
        util += 99
    if(danger_two):
        #print("danger_two")
        util += 99
    if(danger_three):
        #print("danger_three")
        util += 99
    if(danger_four):
        #print("danger_four")
        util += 99
    if(danger_five):
        #print("danger_five")
        util += 99
    if(danger_six):
        #print("danger_six")
        util += 99
    return util

def is_stable(board_state, i, j, player):
    vert = False
    horz = False
    c = (i == 0 and (j == 1 or j == 6)) or (i == 1 and (j == 0 or j == 7)) or (i == 7 and (j == 1 or j == 6)) or (i == 6 and (j == 0 or j ==7))
    a = (i == 0 and (j == 2 or j == 5)) or (i == 2 and (j == 0 or j == 7)) or (i == 7 and (j == 2 or j == 5)) or (i == 5 and (j == 0 or j ==7))
    b = (i == 0 and (j == 3 or j == 4)) or (i == 3 and (j == 0 or j == 7)) or (i == 7 and (j == 3 or j == 4)) or (i == 4 and (j == 0 or j ==7))
    i2 = i
    j2 = j
    while(i2 <= 7):
        if(board_state[i2][j] == player):
            if(i2 == 7):
                vert = True
            i2 = i2 + 1
        else:
            break
    i2 = i
    if(not vert):
        while(i2 >= 0):
            if(board_state[i2][j] == player):
                if(i2 == 0):
                    vert = True
                i2 = i2 - 1
            else:
                break
    while(j2 <= 7):
        if(board_state[i][j2] == player):
            if(j2 == 7):
                horz = True
            j2 = j2 + 1
        else:
            break
    j2 = j
    if(not horz):
        while(j2 >= 0):
            if(board_state[i][j2] == player):
                if(j2 == 0):
                    horz = True
                j2 = j2 - 1
            else:
                break
    if(vert and horz):
        if(a or b):
            return 1000
        if(c):
            return 1200
    if(semi_stable(board_state, i, j)):
        return 200
    else:
        if(a):
            return 75
        if(b):
            return 50
        if(c):
            return -25

def semi_stable(current_state, i, j):
    if i < 7 and i > 0:
        if(current_state[i+1][j] == opponent):
            i2 = i
            while(i2 > 0):
                i2 = i2 - 1
                if(current_state[i2][j] == me):
                    continue;
                elif(current_state[i2][j] == 0):
                    return False
                else:
                    break

        if(current_state[i-1][j] != opponent):
            i2 = i
            while(i2 < 7):
                i2 += 1
                if(current_state[i2][j] == me):
                    continue;
                elif(current_state[i2][j] == 0):
                    return False
                else:
                    break

    if j < 7 and j > 0:
        if(current_state[i][j+1] != opponent):
            j2 = j
            while(j2 > 0):
                j2 = j2 - 1
                if(current_state[i][j2] == me):
                    continue;
                elif(current_state[i][j2] == 0):
                    return False
                else:
                    break
        if(current_state[i][j-1] != opponent):
            j2 = j
            while(j2 < 7):
                j2 = j2 + 1
                if(current_state[i][j2] == me):
                    continue;
                elif(current_state[i][j2] == 0):
                    return False
                else:
                    break
    return True

def stable_disk_util(current_state, player):
    stable_disks = 0;
    for i in range(8):
        for j in range(8):
            stable_disks = stable_disks + 1*is_stable(current_state, i, j, player)

    #print(stable_disks)
    return stable_disks

# Mimics doing specified move on current state
# Returns a new board state
def new_board_state(current_state, player, current_move):
    new_state = copy.deepcopy(current_state)
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
        opponent = 2 if me == 1 else 1
        play_game(sys.argv[1])
    else:
        print("USAGE: python3 RandomGuy.py [ip address] [1,2]")
