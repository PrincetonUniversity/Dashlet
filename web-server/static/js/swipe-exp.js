var player = dashjs.SuperPlayer().create();

var view = document.getElementById('example-video');

// var serverip = "{{ serverip }}";

console.log("serverip");
console.log(typeof(serverip));
console.log(serverip);
console.log("serverip");

var cdnaddress = 'http://'+serverip+':8080/dash/data/';

var thisVideo = 'startvideo';
var requestvideo = '';

var nextVideo = '';
var preVideo = '';
var swaptmp = '';

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const traceid = urlParams.get('traceid');

console.log(traceid);

$.getJSON('/getNeighbour', {
    vid: thisVideo,  traceid: traceid}, function(data) {
    preVideo = data.uidPre;
    nextVideo = data.uidNext;
});

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
                vid: requestvideo, traceid: traceid}, function(data) {
                preVideo = data.uidPre;
                nextVideo = data.uidNext;

                thisVideo = requestvideo

                console.log("preVideo: "+ preVideo+"; nextVideo: "+nextVideo);
            });
        }
    }, 500);


player.attachView(view);


var start = null;


function toNextVideo() {

    player.playNext();

}

