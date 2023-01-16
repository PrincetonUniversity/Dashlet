var player = videojs('example-video');

// var player = dashjs.SuperPlayer().create();
// var view = document.getElementById('example-video');

// player.attachView(view);

var cdnaddress = 'http://172.29.130.16:8080/dash/mp4/';


var thisVideo = '5904810145583287557';

var nextVideo = '';
var preVideo = '';
var swaptmp = '';


$.getJSON('/getNeighbour', {
    vid: thisVideo}, function(data) {
    preVideo = data.uidPre;
    nextVideo = data.uidNext;
});



var videoELement = document.getElementById("example-video");



function playPause() {
    if (player.paused()) {
        player.play();
    } else {
        player.pause();
    }
 }

var touchtime = 0;
videoELement.addEventListener("touchstart", function(event) {

    if (touchtime == 0) {
        // set first click
        touchtime = new Date().getTime();
    } else {
        // compare first click to this click and see if they occurred within double click threshold
        if (((new Date().getTime()) - touchtime) < 800) {
            // double click occurred
            // alert("double clicked");
            touchtime = 0;
    
            playPause();
    
    
        } else {
            // not a double click so set as a new first click
            touchtime = new Date().getTime();
        }
    }
    
});



function toNextVideo() {


    $.getJSON('/uploadPlayback', {
        duration: player.duration(),
        currentTime: player.currentTime(),
        vid: thisVideo
    }, function(data) {
    });

    console.log(player.currentTime());
    console.log(player.duration());

    thisVideo = nextVideo;

    player.src({
        src: cdnaddress + thisVideo + '.mp4',
        type: 'video/mp4'
    });

    player.play();

    $.getJSON('/getNeighbour', {
        vid: thisVideo}, function(data) {
        preVideo = data.uidPre;
        nextVideo = data.uidNext;
    });

}


function toPreVideo() {
    thisVideo = preVideo;

    player.src({
        src: cdnaddress + thisVideo + '.mp4',
        type: 'video/mp4'
    });


    player.play();


    $.getJSON('/getNeighbour', {
        vid: thisVideo}, function(data) {
        preVideo = data.uidPre;
        nextVideo = data.uidNext;
    });
}

player.ready(function() {

    player.src({
        src: cdnaddress + thisVideo + '.mp4',
        type: 'video/mp4'
    });

    player.play();


    this.on("ended", function(){
        // alert("ended");
        toNextVideo();
    });


});


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
            // alert("left -> right");

            toPreVideo();

        }


        if(end < start - offset ){
            toNextVideo();
        }
    }

});

