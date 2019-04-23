socket = new WebSocket("ws://127.0.0.1:8000/ws/mpeg/1");

socket.onopen = function() {
    console.log("Connection established");
};

socket.onmessage = function(event) {
    console.log("Got data: " + event.data);
    var elements = document.getElementsByClassName("digit");
    Array.from(elements)
    .map(function (elem) {
        elem.innerHTML = event.data;
    });
};

socket.onclose = function(event) {
    if (event.wasClean) {
        console.log("Connection closed successfully");
    } else {
        console.log("Connection closed unsuccessfully");
    }
    console.log('Code: ' + event.code + ' reason: ' + event.reason);
};

socket.onerror = function(error) {
    console.log("Error: " + error.message);
};
