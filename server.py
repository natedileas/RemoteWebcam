import socket
import threading
import queue
import pickle

class ImageSocket(socket.socket):
    MSG_LEN = 10
    CHUNK = 2048

    def __init__(self):
        super(ImageSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

    def csend(self, obj):
        return _send(self, obj)

    def crecieve(self):
        return _recieve(self)

def _send(sock, obj):
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

class ServerThread(threading.Thread):
    def __init__(self, sock, queue):
        super(ServerThread, self).__init__()
        self.sock = sock
        self.queue = queue
        self.serve = threading.Event()

    def join(self, timeout=None):
        self.serve.set()
        super(ServerThread, self).join(timeout)

    def run(self):
        while not self.serve.isSet():
            try:
                data = _recieve(self.sock)
                self.queue.put(data)

            except RuntimeError:
                self.sock.close()
                print('Connection Closed')
                break

class Server(threading.Thread):
    def __init__(self, hostname, port):
        super(Server, self).__init__()
        self.hostname = hostname
        self.port = port
        self.serve = threading.Event()
        self.queue = queue.Queue()
        self.lock = threading.Lock()

        self._state = {}

    def join(self, timeout=None):
        self.serve.set()
        super(Server, self).join(timeout)

    def run(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.hostname, self.port))
        serversocket.listen(2)   # 2 connection at a time
        serversocket.settimeout(1)   # so self.serve.isSet can actually work

        while not self.serve.isSet():

            try:
                (clientsocket, address) = serversocket.accept()
                print('Connected')
                clientsocket.setblocking(1)
                st = ServerThread(clientsocket, self.queue)
                st.start()
            except socket.timeout:
                continue


def setup(hostname, port):
    server = Server(hostname, port)
    server.start()
    return server
