buttonFold = document.getElementById("foldButton");
buttonCheck = document.getElementById("checkButton");
buttonCall = document.getElementById("callButton");
buttonRaise = document.getElementById("raiseButton");
amountRaise = document.getElementById("raiseAmount");

function updateButtons(user, currentUser){
  if (user == currentUser){
    buttonFold.disabled = false;
    buttonCheck.disabled = false;
    buttonCall.disabled = false;
    buttonRaise.disabled = false;
    amountRaise.disabled = false;
  }else{
    buttonFold.disabled = true;
    buttonCheck.disabled = true;
    buttonCall.disabled = true;
    buttonRaise.disabled = true;
    amountRaise.disabled = true;
  }
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

  socket.emit('connecting', {data: data});
  console.log("Connecting/Connected!");
});

socket.on("response", function(msg, cb){ //when recieving response
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);

  if (parsedResponse["data-type"] == "console message"){
    let message = parsedResponse["message"];
    console.log(message);
  }

  for (i = 1; i <=5; i++){
    document.getElementById("user"+i).innerHTML = parsedResponse["playerList"][i][0];
    document.getElementById("money"+i).innerHTML = "$"+parsedResponse["playerList"][i][1];
  }

  if (parsedResponse["playerList"]['gameState'] == "start"){
    startTurn = parsedResponse["playerList"]['start_turn'];
    start(startTurn, parsedResponse["playerList"]);
    updateButtons(document.getElementById("username").innerHTML, parsedResponse["playerList"][parsedResponse["playerList"]['turn']][0]);
    if (parsedResponse['playerList'][1][0] == username){
      document.getElementById("p1c1").src = parsedResponse['hole1'][0];
      document.getElementById("p1c2").src = parsedResponse['hole1'][1];
    }
    if (parsedResponse['playerList'][2][0] == username){
      document.getElementById("p2c1").src = parsedResponse['hole2'][0];
      document.getElementById("p2c2").src = parsedResponse['hole2'][1];
    }
    if (parsedResponse['playerList'][3][0] == username){
      document.getElementById("p3c1").src = parsedResponse['hole3'][0];
      document.getElementById("p3c2").src = parsedResponse['hole3'][1];
    }
    if (parsedResponse['playerList'][4][0] == username){
      document.getElementById("p4c1").src = parsedResponse['hole4'][0];
      document.getElementById("p4c2").src = parsedResponse['hole4'][1];
    }
    if (parsedResponse['playerList'][5][0] == username){
      document.getElementById("p5c1").src = parsedResponse['hole5'][0];
      document.getElementById("p5c2").src = parsedResponse['hole5'][1];
    }
  }
});

function start(playerTurn, playerList){
  gameStart();
  document.getElementById("dealer"+playerTurn).removeAttribute("hidden");
  document.getElementById("bet"+(playerTurn+1)).innerHTML = "Bet: <br> $50";
  document.getElementById("bet"+(playerTurn+2)).innerHTML = "Bet: <br> $100";
}

function sendFoldMessage(){
  let dict_data = {
    "user" : username
  }
  let data = JSON.stringify(dict_data);
  socket.emit("fold_event", {data: data});
  console.log("folding server");
}

socket.on('fold_response', function(msg){
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);
  console.log(parsedResponse['fold_user'] + " folded")
  if (parsedResponse['next_turn'] == 1){
    document.getElementById("bet5").innerHTML = "FOLDED";
  }else{
    document.getElementById("bet"+(parsedResponse['next_turn']-1)).innerHTML = "FOLDED";
  }
  updateButtons(document.getElementById("username").innerHTML, parsedResponse["next_user"]);
});

function sendCheckMessage(){
  let dict_data = {
    "user" : username
  }
  let data = JSON.stringify(dict_data);
  socket.emit("check_event", {data: data});
  console.log("checking server");
}

function sendCallMessage(){
  let dict_data = {
    "user" : username
  }
  let data = JSON.stringify(dict_data);
  socket.emit("call_event", {data: data});
  console.log("calling server");
}

socket.on('call_response', function(msg){
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);

  if (parsedResponse['next_turn'] == 1){
    document.getElementById("bet5").innerHTML = "Bet:<br>"+parsedResponse['previous_bet'];
  }else{
    document.getElementById("bet"+(parsedResponse['next_turn']-1)).innerHTML = "Bet:<br>$"+parsedResponse['previous_bet'];
  }
  updateButtons(document.getElementById("username").innerHTML, parsedResponse["next_user"]);
});

function sendRaiseMessage(){
  let dict_data = {
    "user" : username
  }
  let data = JSON.stringify(dict_data);
  socket.emit("raise_event", {data: data});
  console.log("raising server");
}

function fold(user){
  console.log("fold");
  sendFoldMessage();
}

buttonFold.addEventListener('click', fold);

function check(){
  console.log("check");
  sendCheckMessage();
}

buttonCheck.addEventListener('click', check);

function call(){
  console.log("call");
  sendCallMessage();
}

buttonCall.addEventListener('click', call);

function raise(){
  console.log("raise");
  sendRaiseMessage();
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
});

soonway = document.getElementById("gamehui");
farway = document.getElementById("lobbyhui");
function gameNotStart(){
  farway.style.visibility = 'visible';
  soonway.style.visibility = 'hidden';
}
function gameStart(){
  farway.style.visibility = 'hidden';
  soonway.style.visibility = 'visible';
}
