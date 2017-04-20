Develeoped and tested with python 3 and opencv 3.2


camera.py: should be run on the machine with the webcam
    - requires opencv
    - depends on server.py

    You'll need to change the hostname variable to the armstrong IP address and pick a nice big port number.


example.py: should be run on the machine you want to do stuff on
    - requires opencv
    - depends on server.py

    Use this as a template, display in whatever framework. I see about a second of lag at about 20 fps with this example tool.
    You'll need to change the hostname variable to the armstrong IP address and pick a nice big port number.

Possible Optimizations: 
    - encode with jpeg or other compression schema?
    - downsample frames
    - lower framerate
    - remove extraneous memory usage?