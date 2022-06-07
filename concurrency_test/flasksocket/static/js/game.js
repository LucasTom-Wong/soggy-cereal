import { io } from "https://cdn.socket.io/4.3.2/socket.io.esm.min.js";

// sending a connect request to the server.
var socket = io.connect('http://localhost:5000');

// An event handler for a change of value
$('input.sync').on('input', function(event) {
  socket.emit('Slider value changed', {
    who: $(this).attr('id'),
    data: $(this).val()
  });
  return false;
});

socket.on('after connect', function(msg) {
  console.log('After connect', msg);
});

socket.on('update value', function(msg) {
  console.log('Slider value updated');
  $('#' + msg.who).val(msg.data);
});
