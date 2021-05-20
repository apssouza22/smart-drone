# Smart drone
Using MediaPipe with the Tello Drone to take selfies. This program gets the video stream from the Tello camera, processes it to make the drone follow the person's face and recognize poses to control the drone.  

## Inspiration
This project was highly inspired by [Tello-openpose](https://github.com/geaxgx/tello-openpose) but totally rewritten focusing in simplicity. Everything should work out of the box.
- Replaced Openpose by MediaPipe
- Removed multiprocessing support
- Replaced pynput by pygame

## Libraries and packages

### OpenCV, pygame, MediaPipe : 
Mainly used for the UI (display windows, read keyboard events, play sounds). Any recent version should work.

### simple-pid :
A simple and easy to use PID controller in Python.
https://github.com/m-lundberg/simple-pid

Used here to control the yaw, pitch, rolling and throttle of the drone. 

The parameters of the PIDs may depend on the processing speed and need tuning to adapt to the FPS you can get. For instance, if the PID that controls the yaw works well at 20 frames/sec, it may yield oscillating yaw at 10 frames/sec.  
