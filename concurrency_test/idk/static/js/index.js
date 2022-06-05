// import * from
const ws = new WebSocket('ws://localhost:8080');
let text_box = document.getElementById("core");
let simple_button = document.getElementById("simple");
let user_num = document.getElementById("num");
let join_button = document.getElementById("join");
let errortext = document.getElementById("error");

ws.onmessage = function(event){
  console.log("received data!");
  let data_recieved = JSON.parse(event.data);
  //content = text_box.innerHTML = event.data;
  if (data_recieved["data-type"] == "user-num-return"){
    update_user_number(data_recieved);
  }
  if (data_recieved["data-type"] == "error"){
    update_error(data_recieved);
  }
  if (data_recieved["data-type"] == "text-return"){
    update_text(data_recieved);
  }
}

let update_text = function(data){
  let new_text = data["data"];
  console.log("New message!!");
  text_box.innerHTML = new_text;
}

let update_error = function(data){
  let new_text = data["error"];
  console.log("New error!!");
  errortext.innerHTML = new_text;
}

let update_user_number = function(data){
  let new_num = data["user-num"];
  console.log("New number is : " + new_num);
  user_num.innerHTML = "User #" + new_num;
}

let say_hi = function(){
  console.log("Button pressed.");
  let dict_data  = {
    "data-type" : "button-response",
    "user" : user_num.innerHTML,
    "value" : "hello-message"

  }
  let data = JSON.stringify(dict_data);
  ws.send(data);
}

let join = function(){
  console.log("Joining!!!");
  let dict_data = {
    "data-type" : "joining"
  }
  let data = JSON.stringify(dict_data);
  ws.send(data);
}

simple_button.addEventListener('click', say_hi);
join_button.addEventListener('click', join);
