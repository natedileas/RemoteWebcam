import socket
import threading
import queue
import pickle

import numpy
import cv2

class ImageSocket(socket.socket):
    """ Provide a simple tcp socket for the transfer of python objects

    Author: Nathan Dileas, 2017, ndileas@gmail.com
    No warranty, no license, just reference me.
    """

    MSG_LEN = 8
    CHUNK = 2048

    def __init__(self):
        super(ImageSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

    def csend(self, obj):
        return _send(self, obj)

    def crecieve(self):
        return _recieve(self)

def _send(sock, obj):
    """ Send a message with pickle serialization. 

    Args:
        sock: open socket to send data on

    """
    totalsent = 0
    msg = pickle.dumps(obj)
    msglen = str(len(msg)).zfill(ImageSocket.MSG_LEN).encode()
    whole_msg = msglen + msg

    while totalsent < len(whole_msg):
        sent = sock.send(whole_msg[totalsent:])

        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent += sent

def _recieve(sock):
    """ Recieve a message with pickle serialization. 

    Args:
        sock: open socket to receive data on

    Returns:
        stuff: pickle deserialized message

    Raises:
        RuntimeError: if no data to be received on socket.
    """
    msglen = sock.recv(ImageSocket.MSG_LEN).decode()

    if len(msglen) == 0:
        raise RuntimeError('msglen 0')

    msglen = int(msglen)

    chunks = []
    bytes_recd = 0
    while bytes_recd < msglen:
        chunk = sock.recv(min(msglen - bytes_recd, ImageSocket.CHUNK))
        if chunk == '':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    
    data = b''.join(chunks)

    if len(data) == 0:
        raise RuntimeError('no data recv\'d')

    stuff = pickle.loads(data)
    
    return stuff


class RemoteCamThread(threading.Thread):
    """ Act as the backend to RemoteCamera (serverside)

    An example use of this class is available in the test harness in this file.

    Author: Nathan Dileas, 2017, ndileas@gmail.com
    No warranty, no license, just reference me.
    """
    def __init__(self, sock):
        super(RemoteCamThread, self).__init__()
        self.sock = sock
        self.serve = threading.Event()
        self.jpg_quality = 75

    def join(self, timeout=None):
        self.serve.set()
        super(RemoteCamThread, self).join(timeout)

    def run(self):
        camID = _recieve(self.sock)
        self.camera = cv2.VideoCapture(camID)

        try:
            while not self.serve.isSet():
                
                data = _recieve(self.sock)
                response = None

                if data == 'read':
                    flag, frame = self.camera.read()
                    eflag, eframe = cv2.imencode('.jpg', frame, \
                        [int(cv2.IMWRITE_JPEG_QUALITY), self.jpg_quality])
                    response = (flag, eframe)

                elif data == 'open':
                    retval = self.camera.open()
                    response = retval

                elif data == 'isOpened':
                    retval = self.camera.isOpened()
                    response = retval

                elif data == 'grab':
                    retval = self.camera.grab()
                    response = retval

                elif data == 'retrieve':
                    flag, frame = self.camera.retrieve()
                    eflag, eframe = cv2.imencode('.jpg', frame)
                    response = (flag, eframe)

                elif 'get' in data:
                    value = self.camera.get(data[1])
                    response = value

                elif 'set' in data:
                    retval = self.camera.set(data[1], data[2])
                    response = retval

                elif 'set_jpeg_quality' in data:
                    self.jpg_quality = data[1]

                elif data == 'release':
                    self.camera.release()
                    break

                if response:
                    _send(self.sock, response)

        except RuntimeError:
            print('RuntimeError: connection lost')
        finally:
            print('Connection Closed')
            self.sock.close()
            self.camera.release()


class Server(threading.Thread):
    """ Dispatch RemoteCamThreads. """
    def __init__(self, hostname, port):
        super(Server, self).__init__()
        self.hostname = hostname
        self.port = port
        self.serve = threading.Event()

    def join(self, timeout=None):
        self.serve.set()
        super(Server, self).join(timeout)

    def run(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.hostname, self.port))
        serversocket.listen(1)   # 1 queued connection at a time
        serversocket.settimeout(1)   # so self.serve.isSet can actually work

        while not self.serve.isSet():

            try:
                (clientsocket, address) = serversocket.accept()
                print('Connected')
                clientsocket.setblocking(1)
                st = RemoteCamThread(clientsocket)
                st.start()
            except socket.timeout:
                continue


def setup(hostname, port):
    """ Convienience func """
    server = Server(hostname, port)
    server.start()
    return server

if __name__ == '__main__':
    # if this example does not work for you, try:
    # disabling your firewall
    # changing the port #
    # double checking hostname spelling
    HOSTNAME = '129.21.52.194'  # must be changed to machine with webcam IP address or hostname
    PORT = 12456    # int, > 4 digits, < 65555

    s = Server(HOSTNAME, PORT)
    s.run()   # not start() intentionally, keeps it alive