import pygame
import random
from time import sleep
from setup import *

pygame.font.init()
win = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
pygame.display.set_caption('Tetris')

class Piece():
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shapeColors[shapes.index(shape)]
        self.rotation = 0

class Theme(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color, value):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.value = value
        self.rectangle = pygame.Rect(x, y, size, size)
        
    def update(self, to_change):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rectangle.collidepoint(event.pos):
                    to_change = self.value
                

def createGrid(possiblePositions = {}):
    grid = [[BLACK for x in range(W_WIDTH // BLOCKSIZE)] for x in range(W_HEIGHT // BLOCKSIZE)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in possiblePositions:
                c = possiblePositions[(j, i)]
                grid[i][j] = c
    return grid
     
def chooseShape():
    return Piece(5, 0, random.choice(shapes))

def drawGrid(surface, row, col):
# This function draws the grey grid lines that we see
    sx = topLeft_x
    sy = topLeft_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*BLOCKSIZE), (sx + W_WIDTH, sy + i * BLOCKSIZE))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * BLOCKSIZE, sy), (sx + j * BLOCKSIZE, sy + W_HEIGHT))  # vertical lines

def convertShapeFormat(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
 
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
 
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
 
    return positions

def checkForSpace(shape, grid):
    accepted_positions = [[(j, i) for j in range(W_WIDTH // BLOCKSIZE) if grid[i][j] == (0,0,0)] for i in range(W_HEIGHT // BLOCKSIZE)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convertShapeFormat(shape)
 
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
 
    return True

def checkIfLost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def writeText(text, color, surface):  
    font = pygame.font.SysFont("comicsans", 60, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (topLeft_x + W_WIDTH /2 - (label.get_width()/2), topLeft_y + W_HEIGHT/2 - label.get_height()/2))

def clearRows(grid, locked):
    # need to see if row is clear the shift every other row above down one
    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

def drawNextShape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, TEXT_COLOR)

    sx = topLeft_x + W_WIDTH + label.get_width() / 2
    sy = topLeft_y + W_HEIGHT /2
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * 20, sy + i * 20, 20, 20), 0)

    surface.blit(label, (sx + 10, sy - 30))

def drawWindow(surface, grid, score = 0, last_score = 0):
    surface.fill(BGCOLOR)
     # current score
    font = pygame.font.SysFont('comicsans', 30)
    scoreLabel = font.render('Score: ' + str(score), 1, TEXT_COLOR)
    surface.blit(scoreLabel, (W_WIDTH - scoreLabel.get_width(), S_HEIGHT / 2 - scoreLabel.get_height() / 2 ))
    
    # last score
    h_scoreLabel = font.render('High Score: ' + last_score, 1, TEXT_COLOR)
    surface.blit(h_scoreLabel, (W_WIDTH - h_scoreLabel.get_width(), S_HEIGHT / 2 + h_scoreLabel.get_height() / 2 ))
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (topLeft_x + j* BLOCKSIZE, topLeft_y + i * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE), 0)
 
    # draw grid and border
    drawGrid(surface, W_HEIGHT // BLOCKSIZE, W_WIDTH // BLOCKSIZE)
    pygame.draw.rect(surface, TEXT_COLOR, (topLeft_x, topLeft_y, W_WIDTH, W_HEIGHT), 5)

def updateScore(nscore):
    score = maxScore()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

def maxScore():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score

def chooseTheme(dico, themes, THEME, surface):
    for key in dico:
        theme = Theme(135, S_HEIGHT * 0.75, 50, dico[key][len(dico[key]) - 2], key)
        themes.add(theme)    
    i = 1
    for theme in themes:
        pygame.draw.rect(surface, theme.color, (theme.x * i, theme.y, theme.size, theme.size), 0)
        i += 1   
    for theme in themes:
        theme.update(THEME)      
        
def main(win):
    global grid

    possiblePositions = {}  # (x,y):(255,0,0)
    grid = createGrid(possiblePositions)
    change_piece = False
    run = True
    current_piece = chooseShape()
    next_piece = chooseShape()
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    
    score = 0
    last_score = maxScore()

    while run:
        level_time += clock.get_rawtime()

        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005
                
        fall_speed = 0.27
        
        grid = createGrid(possiblePositions)
        fall_time += clock.get_rawtime()
        clock.tick()
    
        #checking if we lost
        if checkIfLost(possiblePositions):
            writeText(win, "YOU LOST!", TEXT_COLOR)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            updateScore(score) 
            
        # PIECE FALLING CODE
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (checkForSpace(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not checkForSpace(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not checkForSpace(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not checkForSpace(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                if event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece.y += 1
                    if not checkForSpace(current_piece, grid):
                        current_piece.y -= 1

        shape_pos = convertShapeFormat(current_piece)

        # add color of piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1: # If we are not above the screen
                grid[y][x] = current_piece.color
       # IF PIECE HIT GROUND
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                possiblePositions[p] = current_piece.color
            current_piece = next_piece
            next_piece = chooseShape()
            change_piece = False
            score += clearRows(grid, possiblePositions)
            
        drawWindow(win, grid, score, last_score)
        drawNextShape(next_piece, win)
        pygame.display.update()
        # Check if user lost
        if checkIfLost(possiblePositions):
            run = False

def main_menu():
    run = True
    while run:
        win.fill(BGCOLOR)
        writeText('Press Any Key To Play', TEXT_COLOR, win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)
        

    pygame.display.quit()

main_menu()  