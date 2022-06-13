let buttonFold = document.getElementById("foldButton");
let buttonCheck = document.getElementById("checkButton");
let buttonCall = document.getElementById("callButton");
let buttonRaise = document.getElementById("raiseButton");
let room_code = document.getElementById("room_code").innerHTML;
let buttonKick = document.getElementById("kickButton");

console.log(room_code);

function updateButtons(user, currentUser){
  if (user == currentUser){
    buttonFold.disabled = false;
    buttonCheck.disabled = false;
    buttonCall.disabled = false;
    buttonRaise.disabled = false;
  }else{
    buttonFold.disabled = true;
    buttonCheck.disabled = true;
    buttonCall.disabled = true;
    buttonRaise.disabled = true;
  }
}

let username = document.getElementById("username").innerHTML;
function updateUserName(x){ //delete later
  username = x;
}

pot = document.getElementById("pot");
function updatePot(amount){
  potAmount = (pot.innerHTML).slice(1);
  potAmount = parseInt(potAmount);
  pot.innerHTML = "$" + (potAmount+amount);
}

$(document).ready(function() {

let namespace = '/test';
var socket = io(namespace);

let timer = document.getElementById("timer");

function resetTimer(){
  timer.innerHTML = 30;
}

socket.on('connect', function() { //when it connects to the server
  console.log("Attempting to connect!");

  let dict_data  = {
    "user" : username,
    "room" : room_code
  }
  let data = JSON.stringify(dict_data);

  socket.emit('connecting', {data: data});
  console.log("Connecting/Connected!");
  // checkConnected();
});

socket.on("response", function(msg){ //when recieving response
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);

  if (parsedResponse["data-type"] == "console message"){
    let message = parsedResponse["message"];
    console.log(message);
  }

  if (parsedResponse["data-type"] == "Disconnected!"){
    console.log("Someone has disconnected");
  }

  for (i = 1; i <=5; i++){
    document.getElementById("user"+i).innerHTML = parsedResponse["playerList"][i][0];
    document.getElementById("money"+i).innerHTML = "$"+parsedResponse["playerList"][i][1];
  }

  if (parsedResponse["playerList"]['gameState'] == 0){
    buttonKick.disabled=false;
    resetTimer();
    setInterval(timerUpdate, 1000);
    updatePot(150);
    dealerTurn = parsedResponse["playerList"]['dealer'];
    let money2 = (document.getElementById("money"+(dealerTurn+1)).innerHTML).slice(1);
    money2 = parseInt(money2);
    let money3 = (document.getElementById("money"+(dealerTurn+2)).innerHTML).slice(1);
    money3 = parseInt(money3);
    document.getElementById("money"+(dealerTurn+1)).innerHTML = "$"+(money2-50);
    document.getElementById("money"+(dealerTurn+2)).innerHTML = "$"+(money3-100);
    start(dealerTurn, parsedResponse["playerList"]);
    startTurn = parsedResponse['playerList']['turn'];
    console.log(startTurn);
    updateButtons(document.getElementById("username").innerHTML, parsedResponse["playerList"][startTurn][0]);
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

    let playerList = parsedResponse["playerList"];

    if (buttonFold.disabled == false){
      let dict_data = {
        "user": playerList[playerList['dealer']+1][0],
        "new_money": -50,
        'room': room_code
      }
      let data = JSON.stringify(dict_data);
      socket.emit('update_money', {'data': data});
      let dict_data2 = {
        "user": playerList[playerList['dealer']+2][0],
        "new_money": -100,
        'room': room_code
      }
      let data2 = JSON.stringify(dict_data2);
      socket.emit('update_money', {'data': data2});
    }
  }
});

socket.on('endTheGame', function(msg) {
  // let response = msg.data;
  let parsed_response = JSON.parse(msg["data"]);
  endGame(parsed_response["winner"], parsed_response["amountWon"]);
  let sup_data = {
    "username" : username,
    'room' : room_code
  }
  let supper = JSON.stringify(sup_data);

  socket.emit("leave", {data: supper});
})

function start(playerTurn, playerList){
  console.log("Start game")
  gameStart();
  document.getElementById("dealer"+playerTurn).removeAttribute("hidden");
  if (playerTurn == 5){
    document.getElementById("bet1").innerHTML = "$50";
    document.getElementById("bet2").innerHTML = "$100";
  }else if (playerTurn == 4){
    document.getElementById("bet5").innerHTML = "$50";
    document.getElementById("bet1").innerHTML = "$100";
  }else{
    document.getElementById("bet"+(playerTurn+1)).innerHTML = "$50";
    document.getElementById("bet"+(playerTurn+2)).innerHTML = "$100";
  }
}

function sendFoldMessage(){
  let money = pot.innerHTML;
  money = money.slice(1);
  let dict_data = {
    "user" : username,
    "pot" : parseInt(money),
    "room" : room_code
  }
  let data = JSON.stringify(dict_data);
  socket.emit("fold_event", {data: data});
  console.log("folding server");
}

function timerUpdate(){
  if (timer.innerHTML != "-1"){
    timer.innerHTML = parseInt(timer.innerHTML) - 1;
  }
  if (buttonFold.disabled == false){
    if (parseInt(timer.innerHTML) == 0){
      console.log("Timer out");
      sendFoldMessage();
    }
  }
}

// socket.on("checking", function() {
//   setTimeout(
//     function(){
//       checkConnected();
//       console.log("woo");
//     },
//     1000
//   );
// })
//
// function checkConnected(){
//     let dict_data = {
//       "user" : username
//     }
//     let data = JSON.stringify(dict_data);
//     socket.emit("talking", {data: data});
// }


socket.on('fold_response', function(msg){
  resetTimer();
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);

  if (parsedResponse['gameState'] == 1){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
  }else if (parsedResponse['gameState'] == 2){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
    commc4.src = parsedResponse["4"];
  }else if (parsedResponse['gameState'] == 3){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
    commc4.src = parsedResponse["4"];
    commc5.src = parsedResponse['5'];
  }
  console.log(parsedResponse['fold_user'] + " folded")
  document.getElementById("bet"+(parsedResponse['current_turn'])).innerHTML = "FOLDED";
  updateButtons(document.getElementById("username").innerHTML, parsedResponse["next_user"]);
});

function sendKickMessage(){
  if (timer.innerHTML == "-1"){
    let dict_data = {
      "pot" : pot.innerHTML,
      "room" : room_code
    }
    let data = JSON.stringify(dict_data);
    socket.emit("kick_event", {data: data});
    console.log("kicking server");
  }
}

function sendCheckMessage(){
  let dict_data = {
    "user" : username,
    "room" : room_code
  }
  let data = JSON.stringify(dict_data);
  socket.emit("check_event", {data: data});
  console.log("checking server");
}


socket.on('check_response', function(msg){
  resetTimer();
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);
  if (parsedResponse['gameState'] == 1){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
  }else if (parsedResponse['gameState'] == 2){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
    commc4.src = parsedResponse["4"];
  }else if (parsedResponse['gameState'] == 3){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
    commc4.src = parsedResponse["4"];
    commc5.src = parsedResponse['5'];
  }
  updateButtons(document.getElementById("username").innerHTML, parsedResponse["next_user"]);
});

function sendCallMessage(){
  let dict_data = {
    "user" : username,
    "room" : room_code
  }
  let data = JSON.stringify(dict_data);
  socket.emit("call_event", {data: data});
  console.log("calling server");
}

socket.on('call_response', function(msg){
  resetTimer();
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);
  if (parsedResponse['gameState'] == 1){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
  }else if (parsedResponse['gameState'] == 2){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
    commc4.src = parsedResponse["4"];
  }else if (parsedResponse['gameState'] == 3){
    commc1.src = parsedResponse["1"];
    commc2.src = parsedResponse["2"];
    commc3.src = parsedResponse["3"];
    commc4.src = parsedResponse["4"];
    commc5.src = parsedResponse['5'];
  }
  let currentBet = parseInt((document.getElementById("bet"+(parsedResponse['current_turn'])).innerHTML).slice(1));
  let currentMoney = parseInt((document.getElementById("money"+(parsedResponse['current_turn'])).innerHTML).slice(1));
  let betDifference = parseInt(parsedResponse['previous_bet'])-currentBet;
  updatePot(betDifference);
  document.getElementById("money"+(parsedResponse['current_turn'])).innerHTML = "$" + (currentMoney-betDifference);
  document.getElementById("bet"+(parsedResponse['current_turn'])).innerHTML = "$"+parsedResponse['previous_bet'];
  if (buttonFold.disabled == false){
    let dict_data = {
      "user": username,
      "new_money": betDifference,
      "room" : room_code
    }
    let data = JSON.stringify(dict_data);
    socket.emit('update_money', {'data': data});
  }
  updateButtons(document.getElementById("username").innerHTML, parsedResponse["next_user"]);
});

function sendRaiseMessage(){
  let dict_data = {
    "user" : username,
    "room" : room_code
  }
  let data = JSON.stringify(dict_data);
  socket.emit("raise_event", {data: data});
  console.log("raising server");
}

socket.on('raise_response', function(msg){
  resetTimer();
  let response = msg.data;
  let parsedResponse = JSON.parse(msg["data"]);
  let currentBet = parseInt((document.getElementById("bet"+(parsedResponse['current_turn'])).innerHTML).slice(1));
  let currentMoney = parseInt((document.getElementById("money"+(parsedResponse['current_turn'])).innerHTML).slice(1));
  let betDifference = parseInt(parsedResponse['previous_bet'])-currentBet;
  updatePot(betDifference);
  document.getElementById("money"+(parsedResponse['current_turn'])).innerHTML = "$" + (currentMoney-betDifference);
  document.getElementById("bet"+(parsedResponse['current_turn'])).innerHTML = "$"+parsedResponse['previous_bet'];
  if (buttonFold.disabled == false){
    let dict_data = {
      "user": username,
      "new_money": 0-betDifference,
      "room" : room_code
    }
    let data = JSON.stringify(dict_data);
    socket.emit('update_money', {'data': data});
  }
  updateButtons(document.getElementById("username").innerHTML, parsedResponse["next_user"]);
});

function fold(user){
  console.log("fold");
  sendFoldMessage();
}

buttonFold.addEventListener('click', fold);

function kick(){
  console.log("kick");
  sendKickMessage();
}

buttonKick.addEventListener('click', kick);

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

let commc1 = document.getElementById("commc1");
let commc2 = document.getElementById("commc2");
let commc3 = document.getElementById("commc3");
let commc4 = document.getElementById("commc4");
let commc5 = document.getElementById("commc5");

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

function endGame(winner, amountWon){
  console.log("game ended");
  document.getElementById("winner").innerHTML = winner;
  document.getElementById("finPot").innerHTML = amountWon;
  document.getElementById("results").hidden = false;
  document.getElementById("gamehui").hidden = true;
  document.getElementById("lobbyhui").hidden = true;
}
