import cv2
import queue

from Sever import setup

def example_main():
    hostname = '129.21.57.78'
    port = 12456

    server = setup(hostname, port)

    while True:
        try:
            frame = server.queue.get(timeout=1)
        except queue.Empty:
            continue

        cv2.imshow('Example', frame)
        key = cv2.waitKey(20)

        if key == -1:
            continue
        if chr(key) == 'q' or 'Q':
            print('Quitting')
            break

if __name__ == '__main__':
    example_main()