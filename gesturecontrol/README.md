# Smart drone
Using MediaPipe with the Tello Drone to take selfies. This program gets the video stream from the Tello camera, processes it to make the drone follow the person's face and recognize poses to control the drone.  

## Inspiration
This project was highly inspired by [Tello-openpose](https://github.com/geaxgx/tello-openpose) but totally rewritten focusing in simplicity. Everything should work out of the box.
- Replaced Openpose by MediaPipe
- Removed multiprocessing support
- Replaced pynput by pygame
- Added hand gestures commands

