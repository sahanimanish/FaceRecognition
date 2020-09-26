const video = document.querySelector('.player');
const canvas = document.querySelector('.photo');
const ctx = canvas.getContext('2d');
const img_container = document.querySelector('.img_container');
const loader = document.querySelector('.bouncingLoader');
function getVideo() {
  navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    .then(localMediaStream => {
      // console.log(localMediaStream);
      video.srcObject = localMediaStream;
      video.play();
    })
    .catch(err => {
      console.error(`OH NO!!!`, err);
    });
}

function paintToCanvas() {
  const width = video.videoWidth;
  const height = video.videoHeight;
  canvas.width = width;
  canvas.height = height;

  return setInterval(() => {
    ctx.drawImage(video, 0, 0, width, height);
  }, 1000/25);
}
let data_arr=[]
let no_of_phtos=0
function takePhoto() {

  if(no_of_phtos===2){
    alert('These Images are Enough for training')
    document.querySelector("#btn-cap").style.display='none'
    return
  }
  no_of_phtos++
  const data = canvas.toDataURL('image/jpeg');
  data_arr.push(data)
  const link = document.createElement('a');
  link.href = data;
  link.innerHTML = `<img src="${data}" alt="Capture Images" />`;
  img_container.insertBefore(link, img_container.firstChild);
}

getVideo();


async function send_data_to_server(){

  const name=document.querySelector('#inp').value
  if(name===''){
    alert('Fill your Name in input Box')
    return
  }
  img_container.style.display='none'
  loader.style.display='block'
  const data={
    'images_data':data_arr,
    name
  }
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };
  const res = await fetch('http://' + document.domain+'/api/train', options);
  const json = await res.json();
  alert(json.result)
  window.location.assign('http://' + document.domain)
}

video.addEventListener('canplay', paintToCanvas);
