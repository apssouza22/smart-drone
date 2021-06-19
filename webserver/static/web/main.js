/*
 *  Copyright (c) 2015 The WebRTC project authors. All Rights Reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree.
 */

'use strict';

const callButton = document.getElementById('callButton');
const hangupButton = document.getElementById('hangupButton');
const remoteVideo = document.getElementById('remoteVideo');

callButton.disabled = false;
hangupButton.disabled = true;
let startTime;
let video = new VideoStream()

function addListeners() {
    callButton.addEventListener('click', call);
    hangupButton.addEventListener('click', hangup);
    remoteVideo.addEventListener('loadedmetadata', function () {
        console.log(`Remote video videoWidth: ${this.videoWidth}px,  videoHeight: ${this.videoHeight}px`);
    });
    remoteVideo.addEventListener('resize', () => {
        console.log(`Remote video size changed to ${remoteVideo.videoWidth}x${remoteVideo.videoHeight}`);
        // We'll use the first onsize callback as an indication that video has started
        // playing out.
        if (startTime) {
            const elapsedTime = window.performance.now() - startTime;
            console.log('Setup time: ' + elapsedTime.toFixed(3) + 'ms');
            startTime = null;
        }
    });
}

addListeners();

async function call() {
    callButton.disabled = true;
    hangupButton.disabled = false;
    console.log('Starting call');
    startTime = window.performance.now();
    video.start()
}

function hangup() {
    console.log('Ending call');
    video.stop()
    hangupButton.disabled = true;
    callButton.disabled = false;
}