const ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
const suites = ["C", "D", "H", "S"];
const allCards = [];
const cardImages = {};
const cardRatio = 315 / 225;
const cardHeight = 200;
const cardWidth = cardHeight / cardRatio;

for (const rank of ranks) {
  for (const suite of suites) {
    allCards.push(rank + suite);
  }
}

function getImage(path) {
  const image = new Image();
  image.src = path;
  return image;
}

for (const card of allCards) {
  cardImages[card] = getImage("card_svgs/" + card + ".svg");
}

function drawImage(context, image, x, y, width, height) {
  context.drawImage(image, x, y, width, height);
}

function drawCard(context, card, x, y) {
  drawImage(context, cardImages[card], x, y, cardWidth, cardHeight);
}
