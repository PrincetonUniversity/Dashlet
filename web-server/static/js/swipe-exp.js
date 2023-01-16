var player = dashjs.SuperPlayer().create();

var view = document.getElementById('example-video');

// var view;

// // superplayer = dashjs.SuperPlayer().create();
// var videoContainer = document.getElementById('starter-template');
// if (!view) {
//     view = document.createElement('example-video');
//     view.controls = true;
//     videoContainer.appendChild(view);
// }

// 172.29.130.16
// 172.29.114.202
var cdnaddress = 'http://100.64.0.1:8080/dash/data/';

// var cdnaddress = 'http://127.0.0.1:8080/dash/data/';

var thisVideo = '5904810145583287557';
var requestvideo = '';

var nextVideo = '';
var preVideo = '';
var swaptmp = '';



$.getJSON('/getNeighbour', {
    vid: thisVideo}, function(data) {
    preVideo = data.uidPre;
    nextVideo = data.uidNext;
});

// get all the 

// for (var i=0; i<7; i++) {


//     // await new Promise(r => setTimeout(r, 500));

    
// }

var intervalID = setInterval(
    function(){
        var url = cdnaddress + thisVideo + '/manifest.mpd';
        
        var ret = 0;
        
        if (requestvideo != nextVideo) {
            // previous request has returned
            ret = player.attachSource(url);
        }

        console.log("attach source");

        if (ret == 0) {

            requestvideo = nextVideo;
        
            $.getJSON('/getNeighbour', {
                vid: requestvideo}, function(data) {
                preVideo = data.uidPre;
                nextVideo = data.uidNext;

                thisVideo = requestvideo

                console.log("preVideo: "+ preVideo+"; nextVideo: "+nextVideo);
            });
        }
    }, 500);


player.attachView(view);




// player.ready(function() {
//     player.src({
//         src: cdnaddress + thisVideo + '/manifest.mpd',
//         type: 'application/dash+xml'
//     });
//     player.play();
// });


var start = null;


window.addEventListener("touchstart",function(event){

    if (event.touches.length === 1) {
        //just one finger touched
        start = event.touches.item(0).clientX;
    } else {
        //a second finger hit the screen, abort the touch
        start = null;
    }
});

window.addEventListener("touchend",function(event){

    var offset = 100;//at least 100px are a swipe

    if (start) {
        //the only finger that hit the screen left it
        var end = event.changedTouches.item(0).clientX;

        if(end > start + offset){
            

        }


        if(end < start - offset ){

            player.playNext();

        }
    }

});


function toNextVideo() {

    player.playNext();

}

