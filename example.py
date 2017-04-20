import queue

import cv2

import Server


def example_main(hostname, port):    

    server = Server.setup(hostname, port)

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
    HOSTNAME = '129.21.57.78'
    PORT = 12456

    example_main(HOSTNAME, PORT)