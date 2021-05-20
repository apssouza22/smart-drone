import numpy as np
import cv2
from time import time, sleep


class CameraMorse:
    """
        Designed with the Tello drone in mind but could be used with other small cameras.
        When the Tello drone is not flying, we can use its camera as a way to pass commands to the calling script.
        Covering/uncovering the camera with a finger, is like pressing/releasing a button. 
        Covering/uncovering the camera is determined by calculating the level of brightness of the frames received from the camera
        Short press = dot
        Long press = dash
        If we associate series of dots/dashes to commands, we can then ask the script to launch these commands.
    """
    def __init__(self, dot_duration=0.2, dash_duration=None, blank_duration=None, display=False, threshold=40):
        """
            display : True to display to display brightness(time) in an opencv window (via an object RollingGraph)
        """
        # Durations below are in seconds
        # 0 < duration of a dash <= dot_duration 
        self.dot_duration = dot_duration
        # dot_duration < duration of a dash <= dash_duration
        if dash_duration is None:
            self.dash_duration = 3*dot_duration
        else:
            self.dash_duration = dash_duration
        # Released duration. 
        if blank_duration is None:
            self.blank_duration = 3*dot_duration
        else:
            self.blank_duration = blank_duration

        # Dots or dashes are delimited by a "press" action followed by a "release" action
        # In normal situation, the brightness is above 'threshold'
        # When brightness goes below 'threshold' = "press" action
        # Then when brightness goes back above 'threshold' = "release" action
        self.threshold = threshold

        # Dictionary that associates codes to commands 
        self.commands = {}

        # Current status 
        self.is_pressed = False

        # Timestamp of the last status change (pressed/released)
        self.timestamp = 0

        # Current morse code. String composed of '.' and '-'
        code=""


    def define_command(self, code, command, kwargs={}):
        """
            Add a (code, command, args) to the dictionary of the command
            'command' is a python function
            kwargs is a optionnal dictionary of keyword arguments that will be passed to function 'command' 
            when it will be called. Called this way: command(**kwargs)
            Beware that if code1 is a prefix of code2, the command associated to code2 will never be called !
        """
        self.commands[code] = (command, kwargs)

    def is_pressing (self, frame):
        """
            Calculate the brightness of a frame and 
            returns True if the brightness is below 'threshold' (= pressing)
        """
        self.brightness = np.mean(frame)
        return self.brightness < self.threshold

    def check_command(self):
        cmd, kwargs = self.commands.get(self.code, (None,None))
        if cmd: # We have a code corresponding to a command -> we launch the command
            cmd(**kwargs)
            self.code = ""

    def eval(self,frame):
        """
            Analyze the frame 'frame', detect potential 'dot' or 'dash', and if so, check 
            if we get a defined code
            Returns:
            - a boolean which indicates if the "button is pressed" or not,
            - "dot" or "dash"  if a dot or a dash has just been detected, or None otherwise
        """
        if not self.commands: return None

        pressing = self.is_pressing(frame)
        current_time = time()

        detected = None
        if self.is_pressed and not pressing: # Releasing
            if current_time - self.timestamp < self.dot_duration: # We have a dot
                self.code += "."
                detected = "dot"
                self.check_command()
            elif current_time - self.timestamp < self.dash_duration: # We have a dash
                self.code += "-"
                detected = "dash"
                self.check_command()
            else: # The press was too long, we cancel the current decoding
                self.code = ""
            self.is_pressed = False
            self.timestamp = current_time
        elif not self.is_pressed and pressing: # Pressing
            if current_time - self.timestamp > self.blank_duration: # The blank was too long, we cancel the current decoding
                self.code = ""
            self.is_pressed = True
            self.timestamp = current_time
        
        return pressing, detected

if __name__ == "__main__":

    def test(arg=1):
        print("Function test:", arg)

    frame = {"w": 220*np.ones((10,10)), "b": 20*np.ones((10,10))}

    frames =[ "w","w","w","b","w","b","w","w","w","w","w","b","w","b","b","w","w","w"]

    cm = CameraMorse(display=True)
    cm.define_command("..", test)
    cm.define_command(".-", test, {"arg": 2})

    for f in frames:
        print(cm.eval(frame[f]))
        sleep(0.10)
    cv2.waitKey(0)





