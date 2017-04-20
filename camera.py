import cv2
from server import ImageSocket
import time

HOSTNAME = '129.21.57.78'
PORT = 12456

def send_images(framerate=30, encoding=None):
    interval = 1/float(framerate)

    sock = ImageSocket()
    sock.connect((HOSTNAME, PORT))

    cam = cv2.VideoCapture(0)

    try:
        while True:
            start = time.time()
            flag, frame = cam.read()

            if not flag:
                print('No image was read')
                break

            sock.csend(frame)

            elapsed = start - time.time()
            if elapsed < interval:
                time.sleep(round(interval - elapsed - 0.0001, 5))

    except KeyboardInterrupt:
        print('Exiting')
    except ConnectionResetError: 
        print ('Connection Reset')
    finally:
        cam.release()
        sock.close()

if __name__ == '__main__':
    send_images()