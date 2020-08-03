import socket
import threading
import queue
import pickle
import sys
import signal
import time
import pymysql
import select

''' GLOBAL CONSTANTS '''
client_start_port = 60001
client_port = client_start_port
NUM_ARGS = 1
SERVER_IP = "localhost"
SERVER_PORT = 60000
server_sock = None
MSG_TYPE = "MSG_TYPE"
listener = None
cursor = None
db = None
SERVER_RECONNECT_SPEED = 2.5

kill_threads = threading.Event()

def sigint_handler(sig, frame):
    global kill_threads
    global listener
    print()

    kill_threads.set()
    listener.close()
    sys.exit(0)

def getPickledLen(pickled_msg):
    msg_len = len(pickled_msg)
    pickled_msg_len = msg_len.to_bytes(2, "big")
    return pickled_msg_len

def prepareMsg(msg):
    pickled_msg = pickle.dumps(msg)
    pickled_msg_len = getPickledLen(pickled_msg)
    return pickled_msg_len + pickled_msg  # now i am directly concatenating here

def receiveOneMessage(connection):
    msg_len = connection.recv(2)
    msg_len = int.from_bytes(msg_len, "big")
    msg = connection.recv(msg_len)
    return msg, pickle.loads(msg)

def receive_one_msg(connection, addr):
    global kill_threads
    global server_sock

    while True:

        if kill_threads.is_set():
            connection.close()
            return

        try:
            ready = select.select([connection], [], [], 2.0)
            if len(ready[0]) == 0:
                continue
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
            processData(msg["DATA"])
            dict = {MSG_TYPE: "CONFIRMATION"}
            msg = prepareMsg(dict)

            while True:
                try:
                    server_sock.sendall(msg)
                    break
                except:
                    print("Server Down, will try to reconnect...")
                    make_new_server_sock()

            print("Sent Message")

def make_new_server_sock():
    global server_sock

    while True:
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.connect((SERVER_IP, SERVER_PORT))
            dict = {MSG_TYPE: "CLIENT_DETAILS", "CLIENT_NUM": client_num}
            msg = prepareMsg(dict)
            server_sock.sendall(msg)
            break

        except:
            print("Server Down, will try to reconnect...")
            time.sleep(SERVER_RECONNECT_SPEED)
            continue

def processData(data):
    global cursor
    global db

    try:
        cursor.execute(data)
        db.commit()
        return True
    except:
        db.rollback()
        print("Command did not execute - " + str(data))
        return False

def start_receiving():
    global client_port
    global listener
    global kill_listener_thread
    global kill_threads

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
    global cursor
    global db

    if len(sys.argv) != NUM_ARGS + 1:
        print("Invalid Number of arguments")
        print("Given %d, Expected %d" % (len(sys.argv), NUM_ARGS))
        return

    signal.signal(signal.SIGINT, sigint_handler)
    client_num = int(sys.argv[1])

    if client_num == 0:
        db = pymysql.connect("localhost","client0","client0","test0" )
    elif client_num == 1:
        db = pymysql.connect("localhost","client1","client1","test1" )
    elif client_num == 2:
        db = pymysql.connect("localhost","client2","client2","test2" )
    elif client_num == 3:
        db = pymysql.connect("localhost","client3","client3","test3" )
    else:
        print("Invalid Client Number... Please try something between 0-3")
        return

    cursor = db.cursor()

    client_port = client_start_port + client_num

    make_new_server_sock()

    start_receiving()

if __name__ == "__main__":
    start_client()
