# Smart drone

This project leverage from Machine learning/Computer vision and Robotics
to make a low-cost Drone smarter([Tello](https://m.dji.com/ie/shop/tello-series)).


<img src="assets/demo.jpg"/>

[Check out the video](https://youtu.be/a5ddyfV1hxk)


## Features  
- Control the drone by gestures
- People tracking
- People searching
- Sound feedback
- Morse commands using the camera
- Keyboard control
- Drone path monitoring
- Drone path planning
- Video streaming using Webrtc
- Remote control using websocket
- HTML 5 joystick control
- Apple IOS joystick control (check the ios branch)

## Install dependencies
We provide the requirements.txt file with the required Python dependencies but OpenCV and FFMPEG
is tricky to install, and you should check on the internet how to install those properly

```pip install -r requirements.txt```

## How to run 
You don't need to have a drone to play with the project, the project come with a 
simulated option which will use your comera and you will be able to see the drone moving on the path monitoring window.

If you have the Tello drone, you will need to turn off the mock on the `main` function call.

***The path window has to be focused in order to use the keyboard control***

## Libraries and packages

- [OpenCV](https://opencv.org/) - used to process the images 
- [Pygame](https://www.pygame.org/news) - used to show the path monitoring, path planning and keyboard event 
- [MediaPipe](https://mediapipe.dev/) - used to detect the people body
- [simple-pid](https://github.com/m-lundberg/simple-pid) - used to help with PID controller when moving the drone
- [aiortc](https://github.com/aiortc/aiortc) - used for the Web Real-Time Communication (WebRTC)
- [ffmpeg](http://ffmpeg.org/) - used for video streaming 
- [aiohttp](https://docs.aiohttp.org/en/stable/) - used for the async http server

The gesture module was highly inspired by [Tello-openpose](https://github.com/geaxgx/tello-openpose)
 
-----

## Free Advanced Java Course
I am the author of the [Advanced Java for adults course](https://www.udemy.com/course/advanced-java-for-adults/?referralCode=8014CCF0A5A931ADED5F). This course contains advanced and not conventional lessons. In this course, you will learn to think differently from those who have a limited view of software development. I will provoke you to reflect on decisions that you take in your day to day job, which might not be the best ones. This course is for middle to senior developers and we will not teach Java language features but how to lead complex Java projects. 

This course's lectures are based on a Trading system, an opensource project hosted on my [Github](https://github.com/apssouza22/trading-system).

-----
