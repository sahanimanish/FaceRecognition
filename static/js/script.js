const video = document.querySelector('.player');
const canvas = document.querySelector('.photo');
const ctx = canvas.getContext('2d');

namespace = '/live'; 
// console.log('http://' + document.domain + ':' + location.port + namespace);
var socket = io.connect('http://' + document.domain + '.com' + namespace);

socket.on('connect', function () {
  console.log('connection event');
  socket.emit('event', { data: 'Client, Here' });
});

let setIT;
function getVideo() {
  navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    .then(localMediaStream => {
      console.log(localMediaStream);
      
      video.srcObject = localMediaStream;
      video.play();
    })
    .catch(err => {
      console.error(`some error`, err);
    });
}

function stopBothVideoAndAudio(stream) {
  stream.getTracks().forEach(function(track) {
      if (track.readyState == 'live') {
          track.stop();
      }
  });
}

function stopVideo(){
  clearInterval(setIT)
  stopBothVideoAndAudio(video.srcObject)
}

function paintToCanvas() {
  const width = video.videoWidth;
  const height = video.videoHeight;
 
  canvas.width = width;
  canvas.height = height;
  
  
  function sendVideoFrame_() {
    
    ctx.drawImage(video, 0, 0, width,height);
    
    // and send them through websockets
    socket.emit('livevideo', { data: canvas.toDataURL('image/jpeg', 0.7) });  // Send video frame to server
    
  };
  setIT= setInterval(function(){sendVideoFrame_()}, 1000 / 20);



}



video.addEventListener('canplay', paintToCanvas);