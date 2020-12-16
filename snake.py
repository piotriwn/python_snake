import curses
import random
import time
import ctypes
from ctypes import wintypes

MENU_ITEMS = ["Play", "Scoreboard", "Exit"]
RESUME_MENU_ITEMS = ["Resume", "Exit to main menu", "Exit game"]
BOARD_BORDERS = {"topPadding" : 3, "margins" : 1}


# ------------------------------------------------------------------
# modify CMD character font and window size

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
# font.nFont = 8
# font.dwFontSize.X = 8
# font.dwFontSize.Y = 8
# font.FontFamily = 8
# font.FontWeight = 8
font.nFont = 8
font.dwFontSize.X = 16
font.dwFontSize.Y = 16
font.FontFamily = 8
font.FontWeight = 1
font.FaceName = "Terminal"

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
rect = wintypes.SMALL_RECT(0, 0, 30, 30) # (left, top, right, bottom)
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
        for rowIndex, row in enumerate(self.items):
            x = int(self.width/2) - int(len(row)/2)
            y = int(self.height/2)  + rowIndex
            if rowIndex == self.currentPosition:
                screen.attron(curses.color_pair(1))
                screen.addstr(y, x, row)
                screen.attroff(curses.color_pair(1))
            else:
                screen.addstr(y, x, row)


class ResumeMenu(Menu):
    def print_menu(self, screen):
        for rowIndex, row in enumerate(self.items):
            x = int(self.width/2) - int(len(row)/2)
            y = int(0.6*self.height)  + rowIndex
            if rowIndex == self.currentPosition:
                screen.attron(curses.color_pair(1))
                screen.addstr(y, x, row)
                screen.attroff(curses.color_pair(1))
            else:
                screen.addstr(y, x, row)
                
class GameOverMessage:
    def __init__(self, message, height, width, colorPair, rowNumber):
         self.message = message
         self.height = height
         self.width = width
         self.colorPair = colorPair
         self.rowNumber = rowNumber
         self.messageX = int(self.width/2) - int(len(self.message)/2)
         self.messageY = int(0.6*self.height) + self.rowNumber

    def print_message(self, screen):
        screen.attron(curses.color_pair(self.colorPair))
        screen.addstr(self.messageY, self.messageX, self.message)
        screen.attroff(curses.color_pair(self.colorPair))

class Scoreboard:
    def __init__(self, height, width):
        self.scoreList = []
        self.height = height
        self.width = width

    def display_scoreboard(self, screen):
        if len(self.scoreList) == 0:
            msg = "No scores yet!"
            screen.addstr(int(0.1*self.height), int(self.width/2) - int(len(msg)/2), msg)
        else:
            self.sortedList = sorted(self.scoreList, reverse=True)
            x = int(self.width/2) - int(len("SCORES")/2)
            y = int(0.1*self.height)
            screen.attron(curses.color_pair(5))
            screen.addstr(y, x, "SCORES")
            screen.attroff(curses.color_pair(5))
            y += 1
            for rowIndex, row in enumerate(self.sortedList):
                scoreEntry = str(rowIndex+1) + ". " + str(row)
                x = int(self.width/2) - 3
                y += 1
                screen.addstr(y, x,scoreEntry)


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

    def draw_current_score(self, screen, currentScore):
        screen.attron(curses.color_pair(1))
        msg = "Score: " + str(currentScore)
        screen.addstr(0, 0, msg)
        screen.attroff(curses.color_pair(1))

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
        self.score = 0
        
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
            if keyInput == curses.KEY_DOWN and self.direction != "Up":
                # move head one tile down and n-1 segments goes to n-th segment
                self.direction = "Down"
                self.move_down()
            elif keyInput == curses.KEY_UP and self.direction != "Down":
                self.direction = "Up"
                self.move_up()
            elif keyInput == curses.KEY_LEFT and self.direction != "Right":
                self.direction = "Left"
                self.move_left()
            elif keyInput == curses.KEY_RIGHT and self.direction != "Left":
                self.direction = "Right"
                self.move_right()

    def segments_follow(self):
        for i in range(len(self.segments)-1, 0, -1):
            self.segments[i][0] = self.segments[i-1][0]
            self.segments[i][1] = self.segments[i-1][1]

    def move_down(self):
        self.segments_follow()
        self.segments[0][0] += 1

    def move_up(self):
        self.segments_follow()  
        self.segments[0][0] -= 1

    def move_left(self):
        self.segments_follow()
        self.segments[0][1] -= 1

    def move_right(self):
        self.segments_follow()
        self.segments[0][1] += 1

    def eat_apple(self, applePosY, applePosX):
        self.score += 1
        self.length += 1
        self.segments = [[applePosY, applePosX]] + self.segments

    def check_if_ate_tail(self):
        for segment in self.segments[2:]:
            if self.segments[0] == segment:
                return True # True = ate tail
        return False
    
    def check_if_hit_wall(self, lowerBorder, upperBorder, leftBorder, rightBorder):
        if self.segments[0][0] >= lowerBorder or self.segments[0][0] <= upperBorder or self.segments[0][1] >= rightBorder or self.segments[0][1] <= leftBorder:
            return True
        else:
            return False
    
    def check_if_apple_in_snake(self, applePosY, applePosX):
        for segment in self.segments:
            if segment == [applePosY, applePosX]:
                return True
        return False


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

    # white-red pair for displaying "ate tail" message
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)


    # get window size
    h, w = stdscr.getmaxyx()

    # create an instance "menu" of a class "Menu"
    menu = Menu(MENU_ITEMS, h, w)

    # create a scoreboard instance
    scoreboard = Scoreboard(h, w)

    running = True
    while running:
        stdscr.erase()
        menu.print_menu(stdscr)
        stdscr.refresh()

        # get character
        keyPressed = stdscr.getch()

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

                snakeInitialY = random.randint(board.upperBorder + 1, board.lowerBorder - 1)
                snakeInitialX = random.randint(board.leftBorder + 1, board.rightBorder - 1)

                # create a snake instance
                snake = Snake(snakeInitialY, snakeInitialX)

                # create an apple:
                apple = board.get_apple_position() # list [appleY, appleX]
                while snake.check_if_apple_in_snake(apple[0], apple[1]):
                    apple = board.get_apple_position() # list [appleY, appleX]

                # draw an apple:
                board.draw_apple(apple[0], apple[1], stdscr)

                # create resume menu instance
                resumeMenu = ResumeMenu(RESUME_MENU_ITEMS, h, w)

                gameLoop = True
                while gameLoop:

                    # check if apple eaten
                    # if eaten
                    if snake.segments[0] == apple:
                        snake.eat_apple(apple[0], apple[1])
                        apple = board.get_apple_position()
                        while snake.check_if_apple_in_snake(apple[0], apple[1]):
                            apple = board.get_apple_position() # list [appleY, appleX]

                    if snake.check_if_ate_tail(): # if ate tail 
                        ateTailRunning = True
                        scoreboard.scoreList.append(snake.score)
                        snakeAteMessage = GameOverMessage("Snake ate its tail!", h,w,5,0)
                        scoreMessageText = "You scored " + str(snake.score) + " points!"
                        scoreMessage = GameOverMessage(scoreMessageText, h, w, 1, 1)
                        enterContinueMessage = GameOverMessage("Press ENTER to continue...", h, w, 1,2)
                        while ateTailRunning:
                            snakeAteMessage.print_message(stdscr)
                            scoreMessage.print_message(stdscr)
                            enterContinueMessage.print_message(stdscr)
                            keyPressed = stdscr.getch()
                            if keyPressed == curses.KEY_ENTER or keyPressed in [10,13]:
                                ateTailRunning = False
                                gameLoop = False 
                            stdscr.refresh()

                    if snake.check_if_hit_wall(board.lowerBorder, board.upperBorder, board.leftBorder, board.rightBorder): # if hit wall
                        hitWallRunning = True
                        scoreboard.scoreList.append(snake.score)
                        snakeHitMessage = GameOverMessage("Snake hit the wall!", h, w, 5, 0)
                        scoreMessageText = "You scored " + str(snake.score) + " points!"
                        scoreMessage = GameOverMessage(scoreMessageText, h, w, 1, 1)
                        enterContinueMessage = GameOverMessage("Press ENTER to continue...", h, w, 1,2)
                        while hitWallRunning:
                            snakeHitMessage.print_message(stdscr)
                            scoreMessage.print_message(stdscr)
                            enterContinueMessage.print_message(stdscr)
                            keyPressed = stdscr.getch()
                            if keyPressed == curses.KEY_ENTER or keyPressed in [10,13]:
                                hitWallRunning = False
                                gameLoop = False 
                            stdscr.refresh()
                        
                    startTime = time.process_time()
                    curses.halfdelay(1)
                    keyPressed = stdscr.getch()
                    finishTime = time.process_time()
                    duration = int(1000 * round((finishTime-startTime), 4))


                    if keyPressed != curses.ERR: # if ~ no input ready (so: input ready)
                        curses.napms(100 - duration)

                    if keyPressed in [27, 113]:
                        resumeMenu.currentPosition = 0
                        resumeMenuRunning = True
                        while resumeMenuRunning:
                            keyPressed = stdscr.getch()
                            if keyPressed == curses.KEY_UP and resumeMenu.currentPosition > 0:
                                resumeMenu.currentPosition -= 1
                            elif keyPressed == curses.KEY_DOWN and resumeMenu.currentPosition < len(resumeMenu.items) - 1:
                                resumeMenu.currentPosition += 1
                            elif keyPressed == curses.KEY_ENTER or keyPressed in [10,13]: # taken from ASCII
                                if resumeMenu.currentPosition == len(menu.items) - 1: #user pressed exit game
                                    resumeMenuRunning = False
                                    gameLoop = False
                                    running = False
                                elif resumeMenu.currentPosition == 1: # user pressed exit to main menu
                                    scoreboard.scoreList.append(snake.score)
                                    resumeMenuRunning = False
                                    gameLoop = False
                                elif resumeMenu.currentPosition == 0: # user pressed resume
                                    resumeMenuRunning = False
                            else: # no more than 3 options
                                pass
                            resumeMenu.print_menu(stdscr)
                            stdscr.refresh()
                            
                    
                    snake.establish_direction(keyPressed)

                    # flush input buffer
                    curses.flushinp()

                    stdscr.erase()
                    board.draw_borders(stdscr)
                    board.draw_current_score(stdscr, snake.score)
                    board.draw_apple(apple[0], apple[1], stdscr)
                    snake.draw_snake(stdscr)
                    stdscr.refresh()

            elif menu.currentPosition == 1: # pressed Scoreboard
                stdscr.clear()
                scoreboard.display_scoreboard(stdscr)
                scoreboardMenuRunning = True
                while scoreboardMenuRunning:
                    keyPressed = stdscr.getch()
                    if keyPressed == curses.KEY_ENTER or keyPressed in [10,13]:
                        scoreboardMenuRunning =False
            else: # there is no more than 3 options YET
                pass
    
curses.wrapper(main)

# NOTE
# curses uses the terminal's screensize; it doesn't set the terminal's screensize.
