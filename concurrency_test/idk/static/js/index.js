// import * from
const ws = new WebSocket('ws://localhost:8080');
let text_box = document.getElementById("core");
let simple_button = document.getElementById("simple");
let user_num = document.getElementById("num");
let join_button = document.getElementById("join")

ws.onmessage = function(event){
  console.log("received!");
  let data_recieved = JSON.parse(event.data);
  //content = text_box.innerHTML = event.data;
  if (data_recieved["data-type"] == "user-num-return"){
    update_user_number();
  }
  }

let update_user_number = function(){
  let new_num = data_recieved["user-num"];
  console.log("New number is : " + new_num);
  user_num.innerHTML = new_num
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
}

simple_button.addEventListener('click', say_hi);
join_button.addEventListener('click', join);
