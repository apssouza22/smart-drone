var pc = null
class VideoStream {
    negotiate() {
        pc.addTransceiver('video', {direction: 'recvonly'});
        return pc.createOffer().then(function(offer) {
            return pc.setLocalDescription(offer);
        }).then(function() {
            // wait for ICE gathering to complete
            return new Promise(function(resolve) {
                if (pc.iceGatheringState === 'complete') {
                    resolve();
                } else {
                    function checkState() {
                        if (pc.iceGatheringState === 'complete') {
                            pc.removeEventListener('icegatheringstatechange', checkState);
                            resolve();
                        }
                    }
                    pc.addEventListener('icegatheringstatechange', checkState);
                }
            });
        }).then(function() {
            var offer = pc.localDescription;

            return fetch('http://'+window.location.host+'/offer', {
                body: JSON.stringify({
                    sdp: offer.sdp,
                    type: offer.type,
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            });
        }).then(function(response) {
            return response.json();
        }).then(function(answer) {
            console.log(answer)
            return pc.setRemoteDescription(answer);
        }).catch(function(e) {
            alert(e);
        });
    }


    start() {
        var config = {
            sdpSemantics: 'unified-plan'
        };
        //config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
        pc = new RTCPeerConnection(config);

        // connect audio / video
        pc.addEventListener('track', function(evt) {
            if (evt.track.kind == 'video') {
                console.log(evt)
                //window.stream = stream;
                // var video=document.getElementById('video')
                remoteVideo.srcObject = evt.streams[0];
            }
        });

        this.negotiate();
    }

    stop() {
        setTimeout(function() {
            pc.close();
        }, 500);
    }
}