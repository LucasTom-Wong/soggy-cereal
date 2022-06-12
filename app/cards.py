import random
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
suites = ["C", "D", "H", "S"]
allCards = []

for rank in ranks:
  for suite in suites:
    allCards.append("/static/card_svgs/"+rank + suite + ".svg")

random.shuffle(allCards)

def createDeck():
    deck = []
    for rank in ranks:
      for suite in suites:
        deck.append("/static/card_svgs/"+rank + suite + ".svg")
        random.shuffle(deck)
    return deck

def createCardList(player_num):
    cardList = []
    player = 0
    index = 0
    while (player < player_num):
        cardList.append("/static/card_svgs/back.svg")
        cardList.append("/static/card_svgs/back.svg")
        index+=2
        player+=1
    cardList.append(allCards[index])
    cardList.append(allCards[index+1])
    index+=2
    player+=1
    while (player < 5):
        cardList.append("/static/card_svgs/back.svg")
        cardList.append("/static/card_svgs/back.svg")
        player+=1
    print(cardList)
    return cardList
