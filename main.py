#!/usr/bin/python3

import animation
import sys
import curses
import logging
from random import randint
from math import inf

board = []

BOARD_WIDTH = 3
BOARD_HEIGHT = 3

indi_player = 1
indi_opponent = 2

def new_board():
    return [0 for _ in range(BOARD_WIDTH * BOARD_HEIGHT)]

def filled_board(board):
    return all([x > 0 for x in board])

def get_xy(ind, width=BOARD_WIDTH):
    return ind % width, ind // width

def get_index(x, y, width=BOARD_WIDTH):
    return x + (y * width)

def check_victory(board):
    # if only there's a concise way to checking all that column/row is filled
    # i should think about it 
    for row in range(BOARD_WIDTH):
        if board[get_index(row, 0)] == board[get_index(row, 1)] and board[get_index(row, 1)] == board[get_index(row, 2)]:
            if board[get_index(row, 0)] == indi_player:
                return indi_player
            elif board[get_index(row, 0)] == indi_opponent:
                return indi_opponent
    
    for col in range(BOARD_WIDTH):
        if board[get_index(0, col)] == board[get_index(1, col)] and board[get_index(1, col)] == board[get_index(2, col)]:
            if board[get_index(2, col)] == indi_player:
                return indi_player
            elif board[get_index(2, col)] == indi_opponent:
                return indi_opponent

    # diagonals
    if board[get_index(0, 2)] == board[get_index(1, 1)] and board[get_index(1, 1)] == board[get_index(2, 0)]:
        if board[get_index(0, 2)] == indi_player:
            return indi_player
        elif board[get_index(0, 2)] == indi_opponent:
            return indi_opponent
    
    if board[get_index(0, 0)] == board[get_index(1, 1)] and board[get_index(1, 1)] == board[get_index(2, 2)]:
        if board[get_index(0, 0)] == indi_player:
            return indi_player
        elif board[get_index(0, 0)] == indi_opponent:
            return indi_opponent

def dsp_board(board):
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            print({indi_opponent:"X", indi_player:"O", 0:" "}.get(board[get_index(x, y)]) + (" | " if x < BOARD_WIDTH - 1 else ""), end="")
        print( '\n---------' if y < BOARD_HEIGHT - 1 else "\n")

def minimax(board, depth, maximizing):
    score = check_victory(board)

    if score == indi_opponent or score == indi_player:
        return ({
            indi_player: -15,
            indi_opponent: 15
        }.get(score) or 0) + (depth if score == indi_opponent else -depth)
    
    best = None

    if maximizing:
        best = -inf
        
        for i, item in enumerate(board):
            if item > 0:
                continue
            board[i] = indi_opponent
            best = max(best, minimax(board, depth+1, False))
            board[i] = 0
    else:
        best = inf

        for i, item in enumerate(board):
            if item > 0:
                continue
            board[i] = indi_player
            best = min(best, minimax(board, depth+1, True))
            board[i] = 0
    
    return best

def best_move(board):
    board = board.copy()
    best = -inf
    row = -1
    col = -1
    ind = -1

    for i, item in enumerate(board):
        if item > 0:
            continue

        board[i] = indi_player
        move_worth = minimax(board, 0, False)
        board[i] = 0

        if move_worth > best:
            row, col = get_xy(i)
            ind = i
            best = move_worth
    
    return {'row':row, 'col':col, 'ind':ind}

def simple_main():
    global board
    board = new_board()

    print('tic tac toe')
    cpu_turn_first = randint(1, 2) == 1

    while not filled_board(board) and check_victory(board) is None:
        placewhere = 0
        
        if cpu_turn_first:
            print("robot's turn first!")
            board[randint(0, len(board)-1)] = indi_opponent
            cpu_turn_first = False
        
        print("your turn!")
        dsp_board(board)

        while True:
            try:
                placewhere = get_index(*(int(x.strip())-1 for x in input('state your bet (row,col): ').split(',')))
                
                if board[placewhere] != 0:
                    continue

                break
            except (ValueError, IndexError, TypeError):
                pass

        board[placewhere] = indi_player

        if filled_board(board) or check_victory(board) is not None:
            continue

        try:
            board[best_move(board)['ind']] = indi_opponent
            print("robot has made its move")
            dsp_board(board)
        except IndexError:
            pass

    print({indi_player:'you win!', indi_opponent:'you lost', None:'tie'}.get(check_victory(board)))

last_terminal_size = (None, None)
clickables = []

visual_cell_size = 16
visual_text = ""

class VisualCell:
    cell_type = 1
    cur_frame = 0

def render_board(src, visual_board, palette):
    global last_terminal_size, clickables, visual_text

    if last_terminal_size != src.getmaxyx():
        src.clear()
        last_terminal_size = src.getmaxyx()

    ry, rx = src.getmaxyx()
    rx = rx // 2
    ry = ry // 2
    rx -= ((visual_cell_size+2) * BOARD_WIDTH)
    ry -= (((visual_cell_size+2) * BOARD_HEIGHT) // 2)
    
    # raise Exception(f"{rx} {ry}")
    # src.addstr(ry, rx, "おけ、英語が話せない ")
    
    c_rx, c_ry = rx, ry
    
    clickables.clear()

    try:
        src.addstr(ry - 5, rx - 2, visual_text)
    except curses.error:
        pass

    for col in range(BOARD_HEIGHT):
        for row in range(BOARD_WIDTH):
            s_x = c_rx

            try:
                cell = visual_board[get_index(row, col)]
                cell_animation = animation.cells[cell.cell_type]
               
                for i, (x, y) in enumerate(cell_animation):
                    if i >= cell.cur_frame:
                        continue

                    src.addstr(c_ry + y, c_rx + (x*2), " ", palette[cell.cell_type])
                    src.addstr(c_ry + y, c_rx + ((x*2)+1), " ", palette[cell.cell_type])

                c_rx += (visual_cell_size * 2) + 1
                
                if row < BOARD_WIDTH - 1:
                    src.vline(c_ry - 2, c_rx, curses.ACS_VLINE, ((visual_cell_size // 2) * 2) + 6)
            
                c_rx += 1
            except (KeyError, curses.error):
                pass

            clickables.append((s_x, c_ry, c_rx, c_ry + (visual_cell_size + 2)))

        c_rx = rx
        c_ry += visual_cell_size + 1

        if col < BOARD_HEIGHT - 1:
            src.hline(c_ry, c_rx - 2, curses.ACS_HLINE, ((visual_cell_size * BOARD_WIDTH) * 2) + 6)
        
        c_ry += 1

    logging.info(str(clickables))
    src.refresh()
    
def get_intersected_clickable(my, mx):

    for i, clickable in enumerate(clickables):
        x, y, ex, ey = clickable

        if mx >= x and mx <= ex and my >= y and my <= ey:
            return i
 
def setup_palette(pre_palette):
    delicious_palette = {}

    for pair_index, (name, args) in enumerate(pre_palette.items()): 
        # raise Exception(f"{pair_index+1} {''.join([str(x) for x in args])}")
        curses.init_pair(pair_index + 1, *args)
        delicious_palette[name] = curses.color_pair(pair_index + 1)

    return delicious_palette

def get_mouse():
    _, mx, my, _, _ = curses.getmouse()
    return my, mx

def change_visual_text(src, new_text):
    global visual_text
    visual_text = new_text
    src.clear()

def main(src):
    curses.resizeterm(70, 268)
    src.clear()
    src.refresh()

    logging.basicConfig(filename=".log", filemode="w+", format="%(asctime)s - %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    
    global board, visual_text

    board = new_board()
    visual_board = [VisualCell() for x in range(len(board))]
     
    palette = setup_palette({
        indi_opponent: [curses.COLOR_WHITE, curses.COLOR_RED],
        indi_player: [curses.COLOR_WHITE, curses.COLOR_BLUE],
    })

    # logging.info(str(palette))

    src.clear()

    def render():
        render_board(src, visual_board, palette)

    def do_animation(visual_cell):
        src.nodelay(True)

        for _ in range(len(animation.cells[visual_cell.cell_type]) + 1):
            render()
            visual_cell.cur_frame += 1
            src.getch()
            src.timeout(55)
    
    def wait(iterates):
        for _ in range(iterates):
            render()
            src.getch()
            src.timeout(7)

    def robot(first):
        change_visual_text(src, "It's robot's turn!")
        
        ri = None

        if first:
            ri = randint(0, len(board) - 1)
            board[ri] = indi_player
        
        i = best_move(board).get("ind") or 0
        board[i] = indi_opponent
        
        if first:
            board[ri] = 0
        
        visual_board[i].cell_type = indi_opponent
        visual_board[i].cur_frame = 0
        do_animation(visual_board[i]) 
        wait(50)

    def player():
        change_visual_text(src, "It's your turn!")
        
        src.nodelay(False)

        while True:
            render()
            event = src.getch()

            if event != curses.KEY_MOUSE:
                continue
            
            ind = get_intersected_clickable(*get_mouse())

            if ind is None:
                continue

            try:
                board[ind] = indi_player
                visual_board[ind].cell_type = indi_player
                visual_board[ind].cur_frame = 0
                do_animation(visual_board[ind])
                break
            except KeyError:
                pass
        
        wait(50) 

    def can_replay():
        src.nodelay(False)
        in_check = [ord('y'), ord('n')]

        while True:
            render()
            key = src.getch()

            if key not in in_check:
                continue

            return key == in_check[0]

    src.nodelay(True)
    
    change_visual_text(src, "Welcome! The game will be starting shortly...")
    wait(100)

    first_round = True

    while not filled_board(board) and check_victory(board) is None:
        if randint(1, 2) == 1 or not first_round:
            robot(first_round)
        if filled_board(board) or check_victory(board) is not None:
            continue
        player()
        first_round = False

    change_visual_text(src, str({None:"Tie!", indi_player:"You win!", indi_opponent:"You lost"}.get(check_victory(board))))
    wait(150)
    change_visual_text(src, "Would you like to play again? (Y/n) ")
    return can_replay()

def curses_main(src):
    while main(src):
        pass

if __name__ == '__main__':
    try:
        if '--simple' in sys.argv:
            simple_main()
        else:
            # main(None)
            src = curses.initscr()
            curses.curs_set(0)
            curses.mousemask(1)
            curses.wrapper(curses_main)
    except KeyboardInterrupt:
        pass

