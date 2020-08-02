import socket
import threading
import queue
import pickle
import sys
import signal
import time

''' GLOBAL CONSTANTS '''
client_start_port = 60001
client_port = client_start_port
NUM_ARGS = 1
SERVER_IP = "localhost"
SERVER_PORT = 60000
server_sock = None
MSG_TYPE = "MSG_TYPE"
listener = None

kill_threads = threading.Event()

def sigint_handler():
    global kill_threads
    kill_threads.set()
    sys.exit(0)

def getPickledLen(pickled_msg):
    msg_len = len(pickled_msg)
    pickled_msg_len = msg_len.to_bytes(2, "big")
    return pickled_msg_len

def prepareMsg(msg):
    pickled_msg = pickle.dumps(msg)
    pickled_msg_len = getPickledLen(pickled_msg)
    return pickled_msg_len + pickled_msg  # now i am directly concatenating here

def receive_one_msg(connection, addr):
    global kill_threads
    global server_sock

    while not kill_threads.is_set():

        try:
            msg_len = connection.recv(2)
            print("Got message")
            msg_len = int.from_bytes(msg_len, "big")
            original_msg = connection.recv(msg_len)
            msg = pickle.loads(original_msg)

        except:
            print("Connection with " + str(addr) + " failed")
            return

        if msg[MSG_TYPE] == "HEARTBEAT":
            continue

        elif msg[MSG_TYPE] == "ENTRY":
            print(msg["DATA"])
            dict = {MSG_TYPE: "CONFIRMATION"}
            msg = prepareMsg(dict)
            server_sock.sendall(msg)
            print("sent Message")

def receiveOneMessage(connection):
    msg_len = connection.recv(2)
    msg_len = int.from_bytes(msg_len, "big")
    msg = connection.recv(msg_len)
    return msg, pickle.loads(msg)

def start_receiving():
    global client_port
    global listener
    global kill_listener_thread
    global kill_threads

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('', client_port))
    listener.listen()

    while not kill_threads.is_set():
        connection, addr = listener.accept()
        print("Incoming Connection from: " + socket.gethostbyaddr(addr[0])[0])
        # spawn a new thread to receive the message.
        r = threading.Thread(target=receive_one_msg,args=[connection,addr])
        r.start()
    listener.close()

def start_client():
    global client_num
    global client_port
    global server_sock

    if len(sys.argv) != NUM_ARGS + 1:
        print("Invalid Number of arguments")
        print("Given %d, Expected %d" % (len(sys.argv), NUM_ARGS))
        return

    signal.signal(signal.SIGINT, sigint_handler)
    client_num = int(sys.argv[1])
    client_port = client_start_port + client_num

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_sock.connect((SERVER_IP, SERVER_PORT))
        dict = {MSG_TYPE: "CLIENT_DETAILS", "CLIENT_NUM": client_num}
        msg = prepareMsg(dict)
        server_sock.sendall(msg)
    except:
        print("SERVER NOT RUNNING, EXITING...")
        return

    start_receiving()

start_client()
