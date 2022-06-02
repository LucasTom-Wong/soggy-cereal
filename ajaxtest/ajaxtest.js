const speed = 1;
const slate = document.getElementById("slate");
const change = document.getElementById("change");
const ctx = slate.getContext("2d");

const keyStates = {};

let thisx = 250;
let thisy = 250;
let otherx;
let othery;

function clear() {
  ctx.clearRect(0, 0, slate.width, slate.height);
}

function drawDot(x, y) {
  ctx.beginPath();
  ctx.arc(x, y, 50, 0, Math.PI * 2);
  ctx.fill();
}

function moveThis() {
  if (keyStates.ArrowLeft) {
    thisx -= speed;
  }
  if (keyStates.ArrowRight) {
    thisx += speed;
  }
  if (keyStates.ArrowUp) {
    thisy -= speed;
  }
  if (keyStates.ArrowDown) {
    thisy += speed;
  }
}

function getKeyStateSetter(boolean) {
  return function (e) {
    keyStates[e.code] = boolean;
  }
}

let running = true;

function moveOther() {
  if (running) {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {
    const otherxy = this.responseText.split(",");
    otherx = parseInt(otherxy[0]);
    othery = parseInt(otherxy[1]);
  }
  xhttp.open("POST", "coords.py?user_number=" + user_number + "&x=" + thisx + "&y=" + thisy);
  xhttp.send();
  }
}

function draw() {
  moveThis();
  clear();
  ctx.fillStyle = "rgb(255, 0, 255)";
  drawDot(thisx, thisy);
  ctx.fillStyle = "rgb(0, 255, 255)";
  drawDot(otherx, othery);
}

document.addEventListener("keydown", getKeyStateSetter(true));
document.addEventListener("keyup", getKeyStateSetter(false));
window.setInterval(draw, 1);
window.setInterval(moveOther, 100);
