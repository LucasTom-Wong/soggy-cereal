let button = document.getElementById("reset");
let namespace = '/test';
var socket = io(namespace);

function reset(){
  console.log("resetting");
  socket.emit("reset");
}

button.addEventListener('click', reset);
