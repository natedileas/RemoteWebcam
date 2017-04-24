import cv2
import numpy

from server import ImageSocket


class RemoteCamera(object):
    """ Emulate a cv2.VideoCapture Interface over a network.

    As much as possible, this class follows the class documentation here:
    http://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html?highlight=imwrite#videocapture-videocapture

    A couple exceptions:
     - RuntimeErrors may occur as part of normal operation. They mean your
       connection to the machine with the webcam has broken.
     - You can set the quality of the stream with set_jpeg_quality(int)

    An example use of this class is available in the test harness in this file.

    Author: Nathan Dileas, 2017, ndileas@gmail.com
    No warranty, no license, just reference me.
    """
    def __init__(self, camId, hostname, port):
        # set up camera on other machine
        self.connection = ImageSocket()
        self.connection.connect((hostname, port))
        self.connection.csend(camId)

    def read(self):
        self.connection.csend('read')
        flag, eframe = self.connection.crecieve()

        frame = cv2.imdecode(eframe, 1)

        return flag, frame

    def open(self):
        """ open camera for reading """
        self.connection.csend('open')
        retval = self.connection.crecieve()

        return retval

    def isOpened(self):
        """ return true if opened """
        self.connection.csend('isOpened')
        retval = self.connection.crecieve()

        return retval

    def release(self):
        """ release the resources associated with the camera """
        self.connection.csend('release')

    def grab(self):
        """ The methods/functions grab the next frame from video file or camera 
        and return true (non-zero) in the case of success """
        self.connection.csend('grab')
        retval = self.connection.crecieve()

        return retval

    def retrieve(self):
        """ decode and return the just grabbed frame. If no frames has been 
        grabbed (camera has been disconnected, or there are no more frames in 
        video file), the methods return false and the functions return NULL 
        pointer. """
        self.connection.csend('retrieve')
        retval, image = self.connection.crecieve()

        return image

    def get(self, prop):
        self.connection.csend(('get', prop))
        value = self.connection.crecieve()

        return value

    def set(self, prop, newval):
        self.connection.csend(('set', prop, newval))
        flag = self.connection.crecieve()

        return value

    def set_jpeg_quality(self, newval, *args):
        self.connection.csend(('set_jpeg_quality', newval))


if __name__ == '__main__':
    # if this example does not work for you, try:
    # disabling your firewall
    # changing the port #
    # double checking hostname spelling

    import time

    HOSTNAME = '129.21.52.194'   # must be changed to machine with webcam IP address or hostname
    PORT = 12456    # int, > 4 digits, < 65555
    
    cam = RemoteCamera(0, HOSTNAME, PORT)   # create instance

    window = cv2.namedWindow('winname')
    slider = cv2.createTrackbar('JPEG Quality', 'winname', 75, 100, cam.set_jpeg_quality)
    font = cv2.FONT_HERSHEY_SIMPLEX
    t = 0

    while True:
        s = time.time()

        flag, frame = cam.read()
        if not flag: break
        
        cv2.putText(frame, 'Latency: '+str(t), (10,frame.shape[0]-10), font, 0.5, (0, 0, 255))

        cv2.imshow('winname', frame)
        key = cv2.waitKey(10)

        t = round((time.time() - s) * 1000.)

        if key == -1: 
            continue
        elif chr(key) == 'q' or 'Q':
            break

    cam.release()  # explicit is necesary with current implmentation