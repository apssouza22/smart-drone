# Smart drone

Our project aims to redefine the utility of low-cost drones by infusing them with cutting-edge Machine Learning, Computer Vision, and Robotics technologies. We are focused on developing a multifunctional drone system capable of complex autonomous tasks, interactive controls, and real-time data processing, all packaged within an economically feasible model. ([Tello](https://m.dji.com/ie/shop/tello-series)).


<img src="assets/demo.jpg"/>

[Check out the video](https://youtu.be/a5ddyfV1hxk)


## Features  

- Advanced Navigation and Tracking:
  - Autonomous Navigation and Path Planning: Implement sophisticated pathfinding algorithms to navigate challenging environments autonomously.
  - People Tracking and Searching: Utilize computer vision to identify and follow individuals in various settings, enhancing capabilities in security and rescue operations.
- Interactive Control Methods:
  - Gesture-Based Control: Control drone movements and functions through intuitive hand gestures.
  - Keyboard and Joystick Control: Operate the drone using a keyboard or HTML5 and iOS-compatible joysticks for precision and flexibility.
  - Remote Control via WebSocket: Manage drone operations remotely with real-time responsiveness.
- Enhanced Communication and Feedback:
  - Sound Feedback: Use audio cues for interactive feedback and status updates from the drone.
  - Morse Commands via Camera: Send commands to the drone using Morse code, interpreted through visual inputs from the camera.
- Real-Time Data and Video Management:
  - Video Streaming with WebRTC: Stream live video footage directly through WebRTC, enabling real-time visual feedback for monitoring and decision-making.
  - Drone Path Monitoring: Track and record the drone’s flight path to analyze flight patterns and optimize routes.
- Cost-Effective and User-Friendly Design:
  - Focus on integrating cost-effective hardware and open-source software to keep the drone affordable and accessible.
  - Develop an intuitive interface that allows users to easily manage drone settings, monitor flight paths, and analyze data.


## Install dependencies
We provide the requirements.txt file with the required Python dependencies but OpenCV and FFMPEG
is tricky to install, and you should check on the internet how to install those properly

```pip install -r requirements.txt```

## How to run 
You don't need to have a drone to play with the project, the project come with a 
simulated option which will use your comera and you will be able to see the drone moving on the path monitoring window.

If you have the Tello drone, you will need to turn off the mock on the `main` function call.

***The path window has to be focused in order to use the keyboard control***

### If this project helped you, consider leaving a star  and by me a coffee
<a href="https://www.buymeacoffee.com/apssouza"><img src="https://miro.medium.com/max/654/1*rQv8JgstmK0juxP-Kb4IGg.jpeg"></a>


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
