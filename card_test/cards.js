const ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
const suites = ["C", "D", "H", "S"];
const allCards = [];
const cardImages = {};
const cardHeight = 200;

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

function drawImage(context, image, x, y) {
  context.drawImage(image, x, y, image.width * cardHeight / image.height, cardHeight);
}

function drawCard(context, card, x, y) {
  drawImage(context, cardImages[card], x, y, cardHeight);
}
