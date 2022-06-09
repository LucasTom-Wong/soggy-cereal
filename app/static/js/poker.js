buttonFold = document.getElementById("foldButton");
buttonCheck = document.getElementById("checkButton");
buttonCall = document.getElementById("callButton");
buttonRaise = document.getElementById("raiseButton");
amountRaise = document.getElementById("raiseAmount");

function disableButtons(){
  buttonFold.disabled = true;
  buttonCheck.disabled = true;
  buttonCall.disabled = true;
  buttonRaise.disabled = true;
  amountRaise.disabled = true;
}

function enableButtons(){
  buttonFold.disabled = false;
  buttonCheck.disabled = false;
  buttonCall.disabled = false;
  buttonRaise.disabled = false;
  amountRaise.disabled = false;
}

function fold(){
  console.log("fold");
  disableButtons();
}

buttonFold.addEventListener('click', fold);

function check(){
  console.log("check");
  disableButtons();
}

buttonCheck.addEventListener('click', check);

function call(){
  console.log("call");
  disableButtons();
}

buttonCall.addEventListener('click', call);

function raise(){
  console.log("raise");
  disableButtons();
}

buttonRaise.addEventListener('click', raise);

let p1c1 = document.getElementById("p1c1");
let p1c2 = document.getElementById("p1c2");
let p2c1 = document.getElementById("p2c1");
let p2c2 = document.getElementById("p2c2");
let p3c1 = document.getElementById("p3c1");
let p3c2 = document.getElementById("p3c2");
let p4c1 = document.getElementById("p4c1");
let p4c2 = document.getElementById("p4c2");
let p5c1 = document.getElementById("p5c1");
let p5c2 = document.getElementById("p5c2");

function revealCards(){
  $.get("/reveal_cards", function(cards) {
      let cardDict = JSON.parse(cards);
      let numPlayers = cardDict['length'];
      if (numPlayers > 0){
        p1c1.src = cardDict["p1c1"];
        p1c2.src = cardDict["p1c2"];
      }
      if (numPlayers > 1){
        p2c1.src = cardDict["p2c1"];
        p2c2.src = cardDict["p2c2"];
      }
      if (numPlayers > 2){
        p3c1.src = cardDict["p3c1"];
        p3c2.src = cardDict["p3c2"];
      }
      if (numPlayers > 3){
        p4c1.src = cardDict["p4c1"];
        p4c2.src = cardDict["p4c2"];
      }
      if (numPlayers > 4){
        p5c1.src = cardDict["p5c1"];
        p5c2.src = cardDict["p5c2"];
      }
    });
}

let commc1 = document.getElementById("commc1");
let commc2 = document.getElementById("commc2");
let commc3 = document.getElementById("commc3");
let commc4 = document.getElementById("commc4");
let commc5 = document.getElementById("commc5");

function revealFlop(){
  $.get("/flop", function(flop) {
      let flopDict = JSON.parse(flop);
      commc1.src = flopDict["1"];
      commc2.src = flopDict["2"];
      commc3.src = flopDict["3"];
    });
}

function revealTurn(){
  $.get("/turn", function(turn) {
      let turnDict = JSON.parse(turn);
      commc4.src = turnDict["1"];
    });
}

function revealRiver(){
  $.get("/river", function(river) {
      let riverDict = JSON.parse(river);
      commc5.src = riverDict["1"];
    });
}

let username = document.getElementById("username").innerHTML;
function updateUserName(x){ //delete later
  username = x;
}

$(document).ready(function() {

let namespace = '/test';
var socket = io(namespace);

socket.on('connect', function() { //when it connects to the server
  console.log("Attempting to connect!");
  let dict_data  = {
    "user" : username
  }
  let data = JSON.stringify(dict_data);

  socket.emit('my_event', {data: data});
  console.log("Connecting/Connected!");
});

socket.on("my_response", function(msg, cb){
  let message = msg.data;
  //JSON.parse(event.data);
  console.log(message);
})

});
