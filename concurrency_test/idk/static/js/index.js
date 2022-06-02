// import * from
const ws = new WebSocket('ws://localhost:8080');
var text_box = document.getElementById("core");
var simple_button = document.getElementById("simple");

// var messages = document.createElement("ul");
ws.onmessage = function(event){
  console.log("received!");
  // {"type": "message"}
  content = text_box.innerHTML = event.data;
  // var messages = document.getElementsByTagName("ul")[0],
  //   message = document.createElement("li"),
  //   content = document.createTextNode(event.data)
  //   message.appendChild(content);
  //   messages.appendChild(message);
  }
// document.body.appendChild(messages);

let reply = function(){
  console.log("Button pressed.");
  let dict_data  = {
    "data-type" : "button-response",
    "value" : "hello-message"
  }
  var dict = {
    "data-type" : "button-response",
    "value" : "hello-message"
  };
  data = JSON.stringify(dict);
  ws.send(data);
}

simple_button.addEventListener('click', reply);
