const slate = document.getElementById("slate");
const ctx = slate.getContext("2d");

function randomInt(max) {
  return Math.floor(Math.random() * max);
}

function randomItem(list) {
  return list[randomInt(list.length)];
}

function randomRank() {
  return randomItem(ranks);
}

function randomSuite() {
  return randomItem(suites);
}

function randomCard() {
  return randomRank() + randomSuite();
}

function doThing(e) {
  drawCard(ctx, randomCard(), e.offsetX, e.offsetY);
}

slate.addEventListener("click", doThing);
