import curses
import random
import time
import ctypes
from ctypes import wintypes

MENU_ITEMS = ["Play", "Scoreboard", "Exit"]
BOARD_BORDERS = {"topPadding" : 3, "margins" : 1}


# ------------------------------------------------------------------
# modify CMD character font and window size - no idea how this works

LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_FONT_INFOEX(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("nFont", ctypes.c_ulong),
                ("dwFontSize", COORD),
                ("FontFamily", ctypes.c_uint),
                ("FontWeight", ctypes.c_uint),
                ("FaceName", ctypes.c_wchar * LF_FACESIZE)]

font = CONSOLE_FONT_INFOEX()
font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
font.nFont = 8
font.dwFontSize.X = 8
font.dwFontSize.Y = 8
font.FontFamily = 8
font.FontWeight = 8
font.FaceName = "Terminal"

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
rect = wintypes.SMALL_RECT(0, 0, 50, 50) # (left, top, right, bottom)
ctypes.windll.kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(rect))
ctypes.windll.kernel32.SetCurrentConsoleFontEx(
        handle, ctypes.c_long(False), ctypes.pointer(font))

# ------------------------------------------------------------------


class Menu:
    def __init__(self, menuItems, height, width):
        self.items = menuItems
        self.currentPosition = 0
        self.height = height
        self.width = width

    # screen is a stdscr argument
    # height, width is screen size
    def print_menu(self, screen):
        screen.erase()
        for rowIndex, row in enumerate(self.items):
            x = int(self.width/2) - int(len(row)/2)
            y = int(self.height/2)  + rowIndex
            if rowIndex == self.currentPosition:
                screen.attron(curses.color_pair(1))
                screen.addstr(y, x, row)
                screen.attroff(curses.color_pair(1))
            else:
                screen.addstr(y, x, row)

        screen.refresh()

 
        
class Board:
    def __init__ (self, height, width):
        self.height = height
        self.width = width
        self.lowerBorder = self.height-1 - BOARD_BORDERS["margins"]
        self.upperBorder = BOARD_BORDERS["margins"] + BOARD_BORDERS["topPadding"]
        self.leftBorder = BOARD_BORDERS["margins"]
        self.rightBorder = self.width-1 - BOARD_BORDERS["margins"]

    def draw_borders(self, screen):
        for i in range(BOARD_BORDERS["margins"], self.width - BOARD_BORDERS["margins"]):
            screen.attron(curses.color_pair(4))
            screen.addstr(self.lowerBorder, i, "-")
            screen.addstr(self.upperBorder,i, "-")
            screen.attroff(curses.color_pair(4))
        for j in range(1 + BOARD_BORDERS["margins"] + BOARD_BORDERS["topPadding"], self.height-1 - BOARD_BORDERS["margins"]):
            screen.attron(curses.color_pair(4))
            screen.addstr(j, self.leftBorder, "|")
            screen.addstr(j, self.rightBorder, "|")
            screen.attroff(curses.color_pair(4))
        screen.refresh()

    def get_apple_position(self):
        applePosX = random.randint(self.leftBorder+1, self.rightBorder-1) 
        applePosY = random.randint(self.upperBorder+1, self.lowerBorder-1)
        return [applePosY, applePosX]


    def draw_apple(self, applePosY, applePosX, screen):
        screen.attron(curses.color_pair(3))
        screen.addstr(applePosY, applePosX, "-")
        screen.attroff(curses.color_pair(3))
        

class Snake:
    def __init__ (self, initialY, initialX):
        self.length = 1
        self.segments = [[initialY, initialX]]
        self.direction = None
        
    def draw_snake(self, screen):
        for i in self.segments:
            screen.attron(curses.color_pair(2))
            screen.addstr(i[0], i[1], "-")
            screen.attroff(curses.color_pair(2))

    def establish_direction(self, keyInput):
        if keyInput == curses.ERR: # nothing pressed
            if self.direction == "Down":
                self.move_down()
            elif self.direction == "Up":
                self.move_up()
            elif self.direction == "Left":
                self.move_left()
            elif self.direction == "Right":
                self.move_right()
            elif self.direction == None:
                pass
        else:
            if keyInput == curses.KEY_DOWN:
                # move head one tile down and n-1 segments goes to n-th segment
                self.direction = "Down"
                self.move_down()
            elif keyInput == curses.KEY_UP:
                self.direction = "Up"
                self.move_up()
            elif keyInput == curses.KEY_LEFT:
                self.direction = "Left"
                self.move_left()
            elif keyInput == curses.KEY_RIGHT:
                self.direction = "Right"
                self.move_right()
            elif keyInput in [27, 113]:
                pass
                # show menu

    def move_down(self):
        for i in range(len(self.segments)-1, 0, -1):
            self.segments[i][0] = self.segments[i-1][0]
            self.segments[i][1] = self.segments[i-1][1]
        self.segments[0][0] += 1

    def move_up(self):
        for i in range(len(self.segments)-1, 0, -1):
            self.segments[i][0] = self.segments[i-1][0]
            self.segments[i][1] = self.segments[i-1][1]
        self.segments[0][0] -= 1

    def move_left(self):
        for i in range(len(self.segments)-1, 0, -1):
            self.segments[i][0] = self.segments[i-1][0]
            self.segments[i][1] = self.segments[i-1][1]
        self.segments[0][1] -= 1

    def move_right(self):
        for i in range(len(self.segments)-1, 0, -1):
            self.segments[i][0] = self.segments[i-1][0]
            self.segments[i][1] = self.segments[i-1][1]
        self.segments[0][1] += 1

    def eat_apple(self, applePosY, applePosX):
        self.length += 1
        self.segments = [[applePosY, applePosX]] + self.segments

        
        
        


def main(stdscr):
    curses.curs_set(0)

    # deafut color_pair(0) is white on black
    # here we make 1 as black on white
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # white-white pair for drawing snake
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_WHITE)

    # red-red pair for drawing apple
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED)
    
    # blue-blue pair for drawing boundaries
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLUE)


    # get window size
    h, w = stdscr.getmaxyx()

    # create an instance "menu" of a class "Menu"
    menu = Menu(MENU_ITEMS, h, w)



    menu.print_menu(stdscr)

    running = True
    while running:
        # get character
        keyPressed = stdscr.getch()

        stdscr.erase()

        if keyPressed == curses.KEY_UP and menu.currentPosition > 0:
            menu.currentPosition -= 1
        elif keyPressed == curses.KEY_DOWN and menu.currentPosition < len(menu.items) - 1:
            menu.currentPosition += 1
        elif keyPressed == curses.KEY_ENTER or keyPressed in [10,13]: # taken from ASCII
            if menu.currentPosition == len(menu.items) - 1: #user pressed exit
                running = False
            elif menu.currentPosition == 0: # pressed Play
                # create a board instance
                board = Board(h, w)

                snakeInitialY = random.randint(int(0.1*h), int(0.9*h))
                snakeInitialX = random.randint(int(0.1*w), int(0.9*w))

                # create a snake instance
                snake = Snake(snakeInitialY, snakeInitialX)

                # create an apple:
                apple = board.get_apple_position() # list [appleY, appleX]

                # draw an apple:
                board.draw_apple(apple[0], apple[1], stdscr)

                gameLoop = True
                while gameLoop:
                
                    # check if apple eaten
                    # if eaten
                    if snake.segments[0] == apple:
                        snake.eat_apple(apple[0], apple[1])
                        apple = board.get_apple_position()
                                    

                    startTime = time.process_time()
                    curses.halfdelay(1)
                    keyPressed = stdscr.getch()
                    finishTime = time.process_time()
                    duration = int(1000 * round((finishTime-startTime), 4))


                    if keyPressed != curses.ERR:
                        curses.napms(100 - duration)

                    snake.establish_direction(keyPressed)

                    # flush inp buffer
                    curses.flushinp()

                    stdscr.erase()
                    board.draw_borders(stdscr)
                    board.draw_apple(apple[0], apple[1], stdscr)
                    snake.draw_snake(stdscr)
                    stdscr.refresh()

                # board.draw_borders(stdscr)
                # snake.draw_snake(stdscr)

                # stdscr.getch()
                # stdscr.clear()
            elif menu.currentPosition == 1: # pressed Scoreboard
                stdscr.erase()
                stdscr.addstr(0, 0, f"You pressed {menu.items[menu.currentPosition]}")
                stdscr.getch()
                stdscr.erase()
            else: # there is no more than 3 options YET
                pass

        menu.print_menu(stdscr)
        stdscr.refresh()
    

curses.wrapper(main)

# NOTE
# curses uses the terminal's screensize; it doesn't set the terminal's screensize.
