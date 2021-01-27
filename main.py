"""
Auteur : Kamal Chafik
My second snake game, this time using pygames
TODO: add sound (background, eating and gameover)
"""
import pygame
from pygame import *
import random
import sys

# Initialisation
cellSize = 15
cellCount = 40
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
gameScreen = pygame.display.set_mode((cellSize * cellCount, cellSize * cellCount))
fillColor = (100, 210, 70)
darkColor = (100, 200, 70)

loopClock = pygame.time.Clock()

gameUpdate = pygame.USEREVENT
pygame.time.set_timer(gameUpdate, 150)

scoreFont = pygame.font.Font('font/Bellerose.ttf', 15)

# Directions
RIGHT = Vector2(1, 0)
LEFT = Vector2(-1, 0)
UP = Vector2(0, -1)
DOWN = Vector2(0, 1)

# Classes
class FOOD:
    def __init__(self):
        self.cherry = pygame.image.load('images/cherry.png').convert_alpha()
        self.strawberry = pygame.image.load('images/strawberry.png').convert_alpha()
        self.apple = pygame.image.load('images/apple.png').convert_alpha()

        self.randomPick = 0
        self.fruits = [self.apple, self.strawberry, self.cherry]
        self.fruit = self.fruits[self.randomPick]

        self.getFood()

    def drawFood(self):
        foodRect = pygame.Rect(self.position.x * cellSize, self.position.y * cellSize, cellSize, cellSize)
        gameScreen.blit(self.fruit, foodRect)

    def getFood(self):
        self.randomPick = random.randint(0,2)
        self.fruit = self.fruits[self.randomPick]
        self.x = Vector2(random.randint(0, cellCount - 1))
        self.y = Vector2(random.randint(0, cellCount - 1))
        self.position = Vector2(self.x, self.y)


class SNAKE:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0,0)
        self.getBig = False

        self.headUp = pygame.image.load('images/headUP.png').convert_alpha()
        self.headDown = pygame.image.load('images/headDOWN.png').convert_alpha()
        self.headRight = pygame.image.load('images/headRIGHT.png').convert_alpha()
        self.headLeft = pygame.image.load('images/headLEFT.png').convert_alpha()

        self.tailUp = pygame.image.load('images/tailUP.png').convert_alpha()
        self.tailDown = pygame.image.load('images/tailDOWN.png').convert_alpha()
        self.tailRight = pygame.image.load('images/tailRIGHT.png').convert_alpha()
        self.tailLeft = pygame.image.load('images/tailLEFT.png').convert_alpha()

        self.bodyVertical = pygame.image.load('images/bodyVERTICAL.png').convert_alpha()
        self.bodyHorizontal = pygame.image.load('images/bodyHORIZONTAL.png').convert_alpha()

        self.cornerRU = pygame.image.load('images/cornerRU.png').convert_alpha()
        self.cornerRD = pygame.image.load('images/cornerRD.png').convert_alpha()
        self.cornerLU = pygame.image.load('images/cornerLU.png').convert_alpha()
        self.cornerLD = pygame.image.load('images/cornerLD.png').convert_alpha()

        self.head = self.headRight
        self.tail = self.tailRight
        self.corner = self.cornerRU

        self.eatSound = pygame.mixer.Sound('sound/eat.wav')
        self.gameOverSound = pygame.mixer.Sound('sound/gameover.wav')

    def drawSnake(self):
        self.updateHead()
        self.updateTail()

        for index, part in enumerate(self.body):
            xPos = int(part.x * cellSize)
            yPos = int(part.y * cellSize)
            partRect = pygame.Rect(xPos, yPos, cellSize, cellSize)

            if index == 0:
                gameScreen.blit(self.head, partRect)
            elif index == len(self.body) - 1:
                gameScreen.blit(self.tail, partRect)
            else:
                previousPart = self.body[index + 1] - part
                nextPart = self.body[index - 1] - part
                if previousPart.x == nextPart.x:
                    gameScreen.blit(self.bodyVertical, partRect)
                elif previousPart.y == nextPart.y:
                    gameScreen.blit(self.bodyHorizontal, partRect)
                else:
                    if previousPart.x == -1 and nextPart.y == -1 or previousPart.y == -1 and nextPart.x == -1:
                        self.corner = self.cornerRU
                    elif previousPart.x == -1 and nextPart.y == 1 or previousPart.y == 1 and nextPart.x == -1:
                        self.corner = self.cornerRD
                    elif previousPart.x == 1 and nextPart.y == -1 or previousPart.y == -1 and nextPart.x == 1:
                        self.corner = self.cornerLU
                    else:
                        self.corner = self.cornerLD
                    gameScreen.blit(self.corner, partRect)

    def updateHead(self):
        headDirection = self.body[1] - self.body[0]
        if headDirection.x == 1:
            self.head = self.headLeft
        elif headDirection.x == -1:
            self.head = self.headRight
        elif headDirection.y == 1:
            self.head = self.headUp
        else:
            self.head = self.headDown

    def updateTail(self):
        tailDirection = self.body[-2] - self.body[-1]
        if tailDirection.x == -1:
            self.tail = self.tailLeft
        elif tailDirection.x == 1:
            self.tail = self.tailRight
        elif tailDirection.y == -1:
            self.tail = self.tailUp
        else:
            self.tail = self.tailDown

    def moveSnake(self):
        if self.getBig:
            tempBody = self.body[:]
            tempBody.insert(0, self.body[0] + self.direction)
            self.body = tempBody
            self.getBig = False
            self.drawSnake()
        else:
            tempBody = self.body[:-1]
            tempBody.insert(0, self.body[0] + self.direction)
            self.body = tempBody
            self.drawSnake()


class GAME:
    def __init__(self):
        self.snake = SNAKE()
        self.food = FOOD()
        self.game = False
        self.gameBG = pygame.mixer.Sound('sound/background.wav')

    def updateGame(self):
        self.snake.moveSnake()
        self.checkEncounter()
        self.checkBoundaries()
        self.checkCannibalism()

    def drawGame(self):
        self.food.drawFood()
        self.snake.drawSnake()
        self.drawScore()

    def checkEncounter(self):
        if self.food.position == self.snake.body[0]:  # Head position vs Food position
            self.food.getFood()
            self.playSound(1)
            while self.food.position in self.snake.body[:]:
                self.food.getFood()
            self.snake.getBig = True

    def checkBoundaries(self):  # snake needs to stay within
        if not 0 <= self.snake.body[0].x < cellCount or not 0 <= self.snake.body[0].y < cellCount:
            self.playSound(0)
            self.gameReset()

    def checkCannibalism(self):  # snake cant much on itself
        for part in self.snake.body[1:]:
            if part == self.snake.body[0]:
                self.playSound(0)
                self.gameReset()

    def gameReset(self):
        self.snake.direction = Vector2(0,0)
        self.snake.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.game = False

    def gameOver(self):
        pygame.quit()
        sys.exit()

    def drawGrid(self):
        for row in range(cellCount):
            if row % 2 == 0:
                for col in range(cellCount):
                    if col % 2 == 0:
                        gridRect = pygame.Rect(col*cellSize,row*cellSize,cellSize,cellSize)
                        pygame.draw.rect(gameScreen,darkColor,gridRect)
            else:
                for col in range(cellCount):
                    if col % 2 != 0:
                        gridRect = pygame.Rect(col * cellSize, row * cellSize, cellSize, cellSize)
                        pygame.draw.rect(gameScreen, darkColor, gridRect)

    def drawScore(self):
        score = " Score: " + str(len(self.snake.body) - 3)
        scoreSurface = scoreFont.render(score,True,(0,0,0))
        scorePosition = Vector2((cellCount * cellSize) - 50 , 20)
        scoreRect = scoreSurface.get_rect(center = (scorePosition.x, scorePosition.y))
        scoreBG = pygame.Rect(scoreRect.left ,scoreRect.top,scoreRect.width+10,scoreRect.height+2)

        pygame.draw.rect(gameScreen, (0,0,0), scoreBG,2)
        gameScreen.blit(scoreSurface,scoreBG)

    def playSound(self, sound):
        if sound == 0 and self.game:
            self.snake.gameOverSound.play()
        elif sound == 1:
            self.snake.eatSound.play()
        elif sound == 2:
            self.gameBG.play(-1)



# Main game
game = GAME()
game.playSound(2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.gameOver()
        if event.type == gameUpdate:
            game.updateGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game.snake.direction != DOWN:
                game.snake.direction = UP
                game.game = True
            elif event.key == pygame.K_DOWN and game.snake.direction != UP:
                game.snake.direction = DOWN
                game.game = True
            elif event.key == pygame.K_RIGHT and game.snake.direction != LEFT:
                game.snake.direction = RIGHT
                game.game = True
            elif event.key == pygame.K_LEFT and game.snake.direction != RIGHT:
                game.snake.direction = LEFT
                game.game = True

    gameScreen.fill(fillColor)
    game.drawGrid()
    game.drawGame()
    pygame.display.update()
    loopClock.tick(60)
