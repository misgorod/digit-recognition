constraints = {
    video: { width: 300, height: 300 }
}

navigator.mediaDevices.getUserMedia(constraints)
    .then(
        function(stream) {
            var video = document.querySelector('video');
            video.srcObject = stream;
            video.onloadedmetadata = function(e) {
                video.play();
            };
        }
    )
    .catch(
        function(err) {
            console.log(err);
        }
    );

function clicked () {
    console.log("clicked");
    var { blob } = captureVideoFrame("video", "jpeg");
    var fd = new FormData();
    
    fd.append('data', blob);
    
    $.ajax({
        type: 'POST',
        url: "http://localhost:8080/api/image/1",
        data: fd,
        processData: false,
        contentType: false
    })
    .done(function(msg) {
        var elements = document.getElementsByClassName("digit");
        Array.from(elements)
        .map(function (elem) {
            elem.innerHTML = msg;
        });
    })
    .fail(function( jqXHR, textStatus, errorThrown ) {
        alert( "Request failed: " + textStatus + errorThrown );
    })
    .always(function() {
        
    });
};

window.setInterval(function(){
    clicked();
}, 1000);

    
function captureVideoFrame(video, format, quality) {
    if (typeof video === 'string') {
        video = document.getElementById(video);
    }
    
    format = format || 'jpeg';
    quality = quality || 0.92;
    
    if (!video || (format !== 'png' && format !== 'jpeg')) {
        return false;
    }
    
    var canvas = document.createElement("CANVAS");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    var dataUri = canvas.toDataURL('image/' + format, quality);
    var data = dataUri.split(',')[1];
    var mimeType = dataUri.split(';')[0].slice(5)
    
    var bytes = window.atob(data);
    var buf = new ArrayBuffer(bytes.length);
    var arr = new Uint8Array(buf);

    for (var i = 0; i < bytes.length; i++) {
        arr[i] = bytes.charCodeAt(i);
    }

    var blob = new Blob([ arr ], { type: mimeType });
    return { blob: blob, dataUri: dataUri, format: format };
}
