import pygame
from enum import Enum
from random import randint
from copy import copy

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

CARD_WIDTH = int(SCREEN_WIDTH / 15)
CARD_HEIGHT = int(SCREEN_HEIGHT / 5)
INFO_WIDTH = 500
INFO_HEIGHT = 250

COVERED_CARD_SPRITE = pygame.image.load("Sprites/cover.png")
COVERED_CARD_SPRITE = pygame.transform.scale(COVERED_CARD_SPRITE, (CARD_WIDTH, CARD_HEIGHT))
LOST = pygame.image.load("Sprites/lost.png")
LOST = pygame.transform.scale(LOST, (INFO_WIDTH, INFO_HEIGHT))
WON = pygame.image.load("Sprites/won.png")
WON = pygame.transform.scale(WON, (INFO_WIDTH, INFO_HEIGHT))

def getNextSeed(seed):
    if seed == Seed.DENARI:
        return Seed.BASTONI
    elif seed == Seed.BASTONI:
        return Seed.COPPE
    elif seed == Seed.COPPE:
        return Seed.SPADE
    return Seed.DENARI
    
def initializeGame(mazzo, field, playerCards):
    mazzo.shuffle()
    posI = 0
    posJ = 0
    for i in range(36):
        mazzo.cards[i].setPos((posJ * (CARD_WIDTH + SCREEN_WIDTH / 80) + (SCREEN_WIDTH / 25)), (posI * (CARD_HEIGHT + SCREEN_HEIGHT / 40)) + (SCREEN_HEIGHT / 20))
        field[posI].append(mazzo.cards[i])
        field[posI][posJ].covered = True
        posJ += 1
        if posJ == 9:
            field[posI].append(copy(mazzo.getCard(Seed(posI + 1), 10)))
            field[posI][posJ].setPos((posJ * (CARD_WIDTH + SCREEN_WIDTH / 80) + (SCREEN_WIDTH / 25)), (posI * (CARD_HEIGHT + SCREEN_HEIGHT / 40)) + (SCREEN_HEIGHT / 20))
            field[posI][posJ].visible = False
            posJ = 0
            posI += 1
    posI = 36
    for i in range(4):
        mazzo.cards[posI].setPos((10.5 * (CARD_WIDTH + SCREEN_WIDTH / 80) + (SCREEN_WIDTH / 15)), (i * (CARD_HEIGHT + SCREEN_HEIGHT / 40)) + (SCREEN_HEIGHT / 20))
        playerCards.append(mazzo.cards[posI])
        playerCards[i].covered = False
        posI += 1
    checkForKings(playerCards)
    
def checkForKings(playerCards):
    for card in playerCards[:]:
        if card != None and card.value == 10:
            field[Seed.getIndex(card.seed)][9].visible = True
            field[Seed.getIndex(card.seed)][9].covered = False
            playerCards.remove(card)
    
def displayCards(display, field):
    for i in range(4):
        for j in range(10):
            if field[i][j].visible:
                if not field[i][j].covered:
                    display.blit(field[i][j].sprite, (int(field[i][j].x), int(field[i][j].y)))
                else:
                    display.blit(COVERED_CARD_SPRITE, (int(field[i][j].x), int(field[i][j].y)))
                
def displayPlayerCards(display, playerCards):
    for i in range(len(playerCards)):
        if playerCards[i] != None:
            display.blit(playerCards[i].sprite, (int(playerCards[i].x), int(playerCards[i].y)))

def checkForEnding(field):
    lost = True
    for i in range(4):
        if not field[i][9].visible:
            lost = False
    won = True
    for i in range(4):
        for j in range(9):
            if field[i][j].covered:
                won = False
    if lost:
        return 0
    if won:
        return 1
    return 2

class Seed(Enum):

    DENARI = 1
    BASTONI = 2
    COPPE = 3
    SPADE = 4
    
    @classmethod
    def getIndex(cls, type):
        return list(cls).index(type)

class Card:

    def __init__(self, seed, value, sprite):
        self.seed = seed
        self.value = value
        self.sprite = sprite
        self.sprite = pygame.transform.scale(self.sprite, (CARD_WIDTH, CARD_HEIGHT))
        self.covered = True
        self.visible = True
        self.x = 0
        self.y = 0
        
    def setPos(self, x, y):
        self.x = x
        self.y = y
        
    def copy(self, card):
        self.seed = card.seed
        self.value = card.value
        self.sprite = card.sprite
        
    def printCard(self):
        print(self.seed, end = ' ')
        print(self.value)
        
class Mazzo:

    def __init__(self):
        self.cards = []
        currSeed = Seed.DENARI
        currValue = 1
        for i in range(40):
            imgPath = "Sprites/" + str(Seed.getIndex(currSeed) + 1) + str(currValue) + ".png"
            if (currValue == 10):
                imgPath = "Sprites/" + str(Seed.getIndex(currSeed) + 1) + "0.png"
            currSprite = pygame.image.load(imgPath)
            self.cards.append(Card(currSeed, currValue, currSprite))
            currValue += 1
            if currValue == 11:
                currValue = 1
                currSeed = getNextSeed(currSeed)
                
    def shuffle(self):
        newMazzo = []
        while len(self.cards) > 0:
            newMazzo.append(self.cards.pop(randint(0, len(self.cards) - 1)))
        self.cards = newMazzo
        
    def getCard(self, seed, value):
        for i in range(40):
            if self.cards[i].seed == seed and self.cards[i].value == value:
                return self.cards[i]
        return None

pygame.init()

gameDisplay = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Solitario')
clock = pygame.time.Clock()

boardColor = (0, 120, 0)

field = [[] for _ in range(4)]
playerCards = []
mazzo = Mazzo()
initializeGame(mazzo, field, playerCards)

selectedCardIndex = -1

exit = False
endingResult = 2

while not exit:

    gameDisplay.fill(boardColor) 
    displayCards(gameDisplay, field)
    displayPlayerCards(gameDisplay, playerCards)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if endingResult == 2:
                x, y = event.pos
                if selectedCardIndex != -1:
                    for i in range(4):
                        for j in range(9):
                            rect = pygame.Rect(int(field[i][j].x), int(field[i][j].y), CARD_WIDTH, CARD_HEIGHT)
                            if rect.collidepoint(x, y) and Seed.getIndex(playerCards[selectedCardIndex].seed) == i and playerCards[selectedCardIndex].value == j + 1:
                                tempField = Card(field[i][j].seed, field[i][j].value, field[i][j].sprite)
                                tempPlayer = playerCards[selectedCardIndex]
                                field[i][j].copy(tempPlayer)
                                field[i][j].covered = False
                                playerCards[selectedCardIndex].copy(tempField)
                for i in range(len(playerCards)):
                    if playerCards[i] != None:
                        rect = pygame.Rect(int(playerCards[i].x), int(playerCards[i].y), CARD_WIDTH, CARD_HEIGHT)
                        if rect.collidepoint(x, y):
                            selectedCardIndex = i
            else:
                mazzo = Mazzo()
                initializeGame(mazzo, field, playerCards)

    checkForKings(playerCards)
    if (selectedCardIndex >= 0 and selectedCardIndex < len(playerCards)) and playerCards[selectedCardIndex] == None:
        selectedCardIndex = -1
    endingResult = checkForEnding(field)
    if endingResult == 0:
        gameDisplay.blit(LOST,(SCREEN_WIDTH / 2 - INFO_WIDTH / 2, SCREEN_HEIGHT / 2 - INFO_HEIGHT / 2))
    elif endingResult == 1:
        gameDisplay.blit(WON,(SCREEN_WIDTH / 2 - INFO_WIDTH / 2, SCREEN_HEIGHT / 2 - INFO_HEIGHT / 2))

    pygame.display.update()
    clock.tick(60)