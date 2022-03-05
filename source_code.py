import pygame, sys, random
from pygame.locals import *
import queue

BOARDWIDTH = 3
BOARDHEIGHT = 3
TILESIZE = 148
WINDOWWIDTH = 1280
WINDOWHEIGHT = 680
FPS = 30
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BRIGHTBLUE =    (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
GREEN =         (  0, 204,   0)

BGCOLOR = DARKTURQUOISE
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 25

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 9)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 3.5)

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVEBFS_SURF, SOLVEBFS_RECT, SOLVEASTAR_SURF, SOLVEASTAR_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Slide Puzzle")
    BASICFONT = pygame.font.Font("freesansbold.ttf", BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    RESET_SURF, RESET_RECT = makeText("Reset",    BUTTONTEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 220, WINDOWHEIGHT - 150)
    NEW_SURF,   NEW_RECT   = makeText("New Game", BUTTONTEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 220, WINDOWHEIGHT - 115)
    SOLVEBFS_SURF, SOLVEBFS_RECT = makeText("Solve using BFS",    BUTTONTEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 220, WINDOWHEIGHT - 80)
    SOLVEASTAR_SURF, SOLVEASTAR_RECT = makeText("Solve using A*",    BUTTONTEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 220, WINDOWHEIGHT - 45)

    mainBoard = generateNewPuzzle(10)
    SOLVEDBOARD = getStartingBoard() # a solved board is the same as the board in a start state.
    allMoves = [] # list of moves made from the solved configuration

    while True: # main game loop
        slideTo = None # the direction, if any, a tile should slide
        msg = "Click tile or press arrow keys to slide." # contains the message to show in the upper left corner.
        if mainBoard == SOLVEDBOARD:
            msg = "Solved!"

        drawBoard(mainBoard, msg)

        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves) # clicked on Solve button
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard = generateNewPuzzle(10) # clicked on New Game button
                        allMoves = []
                    elif SOLVEBFS_RECT.collidepoint(event.pos):
                        msg = "Solving..."
                        drawBoard(mainBoard, msg)
                        pygame.display.update()
                        init_state = State(mainBoard, None, None)
                        solution_state = BFS(init_state)
                        solution = []
                        if (solution_state != State([], None, None)):
                            solution = []
                            while solution_state.parent_state is not None:
                                checkForQuit()
                                solution.append(solution_state.move)
                                solution_state = solution_state.parent_state
                            solution.reverse()
                            for i in range(len(solution)):
                                slideAnimation(mainBoard, solution[i], "Solving...", animationSpeed=int(TILESIZE / 3))
                                makeMove(mainBoard, solution[i])
                            allMoves = []
                        else:
                            msg = "Can't solve!"
                            drawBoard(mainBoard, msg)
                            pygame.display.update()
                    elif SOLVEASTAR_RECT.collidepoint(event.pos):
                        msg = "Solving..."
                        drawBoard(mainBoard, msg)
                        pygame.display.update()
                        init_state = State(mainBoard, None, None)
                        solution_state = AStar(init_state)
                        solution = []
                        if (solution_state != State([], None, None)):
                            solution = []
                            while solution_state.parent_state is not None:
                                checkForQuit()
                                solution.append(solution_state.move)
                                solution_state = solution_state.parent_state
                            solution.reverse()
                            for i in range(len(solution)):
                                slideAnimation(mainBoard, solution[i], "Solving...", animationSpeed=int(TILESIZE / 3))
                                makeMove(mainBoard, solution[i])
                            allMoves = []
                        else:
                            msg = "Can't solve!"
                            drawBoard(mainBoard, msg)
                            pygame.display.update()
                else:
                    # check if the clicked tile was next to the blank spot

                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                # check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            slideAnimation(mainBoard, slideTo, "Click tile or press arrow keys to slide.", 8) # show slide on screen
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo) # record the slide
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def getStartingBoard():
    # Return a board data structure with tiles in the solved state.
    # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
    # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
    return board


def getBlankPosition(board):
    # Return the x and y of board coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    # This function does not check if the move is valid.
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return a random move from the list of remaining moves
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    left, top = getLeftTopOfTile(tilex, tiley)

    if number == 1:
        image = pygame.image.load("1.png")
    elif number == 2:
        image = pygame.image.load("2.png")
    elif number == 3:
        image = pygame.image.load("3.png")
    elif number == 4:
        image = pygame.image.load("4.png")
    elif number == 5:
        image = pygame.image.load("5.png")
    elif number == 6:
        image = pygame.image.load("6.png")
    elif number == 7:
        image = pygame.image.load("7.png")
    elif number == 8:
        image = pygame.image.load("8.png")

    DISPLAYSURF.blit(image, (left + adjx, top + adjy))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 10, height + 10), 4)
    image = pygame.image.load("tiger.png")
    DISPLAYSURF.blit(image, (1.5 * (BOARDWIDTH * TILESIZE), YMARGIN))
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVEBFS_SURF, SOLVEBFS_RECT)
    DISPLAYSURF.blit(SOLVEASTAR_SURF, SOLVEASTAR_RECT)


def slideAnimation(board, direction, message, animationSpeed):
    # Note: This function does not check if the move is valid.

    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    # prepare the base surface
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the baseSurf Surface.
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        # animate the tile sliding over
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    # From a starting configuration, make numSlides number of moves (and
    # animate these moves).
    board = getStartingBoard()
    drawBoard(board, "")
    pygame.display.update()
    pygame.time.wait(500) # pause 500 milliseconds for effect
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, "Generating new puzzle...", animationSpeed=int(TILESIZE / 3))
        makeMove(board, move)
        lastMove = move
    return board


def resetAnimation(board, allMoves):
    # make all of the moves in allMoves in reverse.
    revAllMoves = allMoves[:] # gets a copy of the list
    revAllMoves.reverse()

    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, "", animationSpeed=int(TILESIZE / 3))
        makeMove(board, oppositeMove)


class State:
    def __init__(self, matrix_state, parent_state, move):
        self.matrix_state = matrix_state
        self.parent_state = parent_state
        self.move = move
        self.g = 0
        self.f = 0


def h(matrix_state):
    distance = 0
    solveBoard = getStartingBoard()
    for i in range(len(matrix_state)):
        for j in range(len(matrix_state[0])):
            if matrix_state[i][j] == 1:
                x_distance = 0 - i
                y_distance = 0 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
            elif matrix_state[i][j] == 2:
                x_distance = 1 - i
                y_distance = 0 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
            elif matrix_state[i][j] == 3:
                x_distance = 2 - i
                y_distance = 0 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
            elif matrix_state[i][j] == 4:
                x_distance = 0 - i
                y_distance = 1 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
            elif matrix_state[i][j] == 5:
                x_distance = 1 - i
                y_distance = 1 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
            elif matrix_state[i][j] == 6:
                x_distance = 2 - i
                y_distance = 1 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
            elif matrix_state[i][j] == 7:
                x_distance = 0 - i
                y_distance = 2 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
            elif matrix_state[i][j] == 8: 
                x_distance = 1 - i
                y_distance = 2 - j
                if x_distance < 0:
                    x_distance = x_distance * -1
                if y_distance < 0:
                    y_distance = y_distance * -1
                distance += x_distance + y_distance
    return distance

def copy_matrix(init_matrix):
    temp = []
    for i in range(len(init_matrix)):
        temp.append([])
        for j in range(len(init_matrix[0])):
            temp[i].append(init_matrix[i][j])
    return temp


def successor(init_state):
    result = []

    if isValidMove(init_state.matrix_state, LEFT):
        temp_matrix = copy_matrix(init_state.matrix_state)
        makeMove(temp_matrix, LEFT)
        temp_state = State(temp_matrix, init_state, LEFT)
        result.append(temp_state)

    if isValidMove(init_state.matrix_state, RIGHT):
        temp_matrix = copy_matrix(init_state.matrix_state)
        makeMove(temp_matrix, RIGHT)
        temp_state = State(temp_matrix, init_state, RIGHT)
        result.append(temp_state)

    if isValidMove(init_state.matrix_state, UP):
        temp_matrix = copy_matrix(init_state.matrix_state)
        makeMove(temp_matrix, UP)
        temp_state = State(temp_matrix, init_state, UP)
        result.append(temp_state)

    if isValidMove(init_state.matrix_state, DOWN):
        temp_matrix = copy_matrix(init_state.matrix_state)
        makeMove(temp_matrix, DOWN)
        temp_state = State(temp_matrix, init_state, DOWN)
        result.append(temp_state)
    
    return result


def BFS(init_state):
    Q = queue.Queue()
    lvl = queue.Queue()
    solveBoard = getStartingBoard()
    Q.put(init_state)
    lvl.put(init_state)
    while not Q.empty():
        checkForQuit()
        current_state = Q.get()

        if current_state.matrix_state == solveBoard:
            return current_state
        
        result = successor(current_state)
        
        for i in range(len(result)):
            checkForQuit()
            flag = 0
            for j in range(lvl.qsize()):
                checkForQuit()
                if (result[i].matrix_state == lvl.queue[j].matrix_state):
                    flag = 1
                    break
            if flag == 0:
                Q.put(result[i])
                lvl.put(result[i])

    return State([], None, None)


def AStar(init_state):
    solveBoard = getStartingBoard()
    init_state.f = h(init_state.matrix_state)
    closed = []
    Q = [init_state]
    while len(Q) > 0:
        current_state = Q.pop(0)

        if current_state.matrix_state == solveBoard:
            return current_state
        
        closed.append(current_state)

        result = successor(current_state)
        for i in range(len(result)):
            result[i].g = current_state.g + 1
            result[i].f = result[i].g + h(result[i].matrix_state)
            flag = 0
            for j in range(len(closed)):
                if result[i].matrix_state == closed[j].matrix_state:
                    flag = 1
                    break
                if flag == 0:
                    for j in range(len(Q)):
                        if result[i].matrix_state == Q[j].matrix_state:
                            flag = 1
                            if result[i].f < Q[j].f:
                                Q[j].g = result[i].g
                                Q[j].f = result[i].f
                                break
            if flag == 0:
                Q.append(result[i])
        Q.sort(key=lambda x: x.f, reverse=False)
    return State([], None, None)
    
if __name__ == "__main__":
    main()





