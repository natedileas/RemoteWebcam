# RemoteWebcam

A simple class to access a remote webcam as if it were a cv2.VideoCapture instance.


### Notes
 - `camera.py` should be run on the machine you want to get frames on, and contains the main class and an example in the test harness
 - `server.py` should be run on the machine that has the webcam
 - Use this as a template, display in whatever framework. I see about a 120 ms of lag at a decent jpeg quality value.
 - You'll need to change the hostname variable to webcam machine's IP address and pick a nice big port number in both files.
 - Develeoped and tested with python 3 and opencv 3.2

### Possible Optimizations: 
- other compression schema?
- downsample frames
- lower framerate
    
No warranty or license, just credit me. Email: ndileas@gmail.com
