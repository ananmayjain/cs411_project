import socket
import threading
import queue
import pickle
import signal
import sys
import time
import select

''' GLOBAL CONSTANTS '''
NUM_CLIENTS = 4
client_ips = ["localhost", "localhost", "localhost", "localhost"]
client_ports = [60001, 60002, 60003, 60004]
SERVER_PORT = 60000
INITIAL_RECEIVE_LEN = 5
CONFIRMATION_TIMEOUT = 10
MSG_TYPE = "MSG_TYPE"
WAKE_UP_THREAD_TIME_INTERVAL = 5.0

''' SHARED VARIABLES '''
client_socks = []
client_queues = []
active_nodes = []
client_thread_conditions = []
client_receive_conditions = []

kill_threads = threading.Event()


def sigint_handler(sig, frame):
    global kill_threads
    print()
    kill_threads.set()

    for i in range(len(client_thread_conditions)):

        client_thread_conditions[i].acquire()
        client_thread_conditions[i].notify()
        client_thread_conditions[i].release()

        client_receive_conditions[i].acquire()
        client_receive_conditions[i].notify()
        client_receive_conditions[i].release()

    sys.exit(0)

def getPickledLen(pickled_msg):
    msg_len = len(pickled_msg)
    pickled_msg_len = msg_len.to_bytes(2, "big")
    return pickled_msg_len

def prepareMsg(msg):
    pickled_msg = pickle.dumps(msg)
    pickled_msg_len = getPickledLen(pickled_msg)
    return pickled_msg_len + pickled_msg

def pushData(client_num, data):
    # No need for locks as Python Queues are Thread safe
    global client_queues
    client_queues[client_num].put(data)

def wakeUpThreads():
    global client_thread_conditions
    global kill_threads

    if kill_threads.is_set():
        return

    threading.Timer(WAKE_UP_THREAD_TIME_INTERVAL, wakeUpThreads).start()

    for i in range(NUM_CLIENTS):
        with client_thread_conditions[i]:
            client_thread_conditions[i].notify()

def sendClientData(client_num):
    global client_socks
    global client_thread_conditions
    global client_receive_conditions
    global client_queues

    sock = client_socks[client_num]
    thread_condition = client_thread_conditions[client_num]
    receive_condition = client_receive_conditions[client_num]
    queue = client_queues[client_num]
    data = None

    while True:

        with thread_condition:

            thread_condition.wait()
            # System has exited
            if kill_threads.is_set():
                print("Quiting Thread " + str(client_num))
                break

            # If Connection not yet established, try to connect again
            # On success proceed, on failure continue and try again next time
            if client_socks[client_num] == None:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    test_sock.connect((client_ips[client_num], client_ports[client_num]))
                    sock = test_sock
                    client_socks[client_num] = sock
                except:
                    print("Unable to Connect to " + str(client_num))
                    continue

            # if queue is not empty, send data, only remove items from queue after confirmation
            if data == None:
                if queue.empty():
                    continue
                data = queue.get()

            dict = {MSG_TYPE: "ENTRY", "DATA": data}
            msg = prepareMsg(dict)

            try:
                sock.sendall(msg)
            except Exception as e:
                # send failed
                print("Connection lost with " + str(client_num))
                print("Will Initiate reconnection on next try")
                sock.close()
                sock = None
                continue

            with receive_condition:
                if not receive_condition.wait(CONFIRMATION_TIMEOUT):
                    print("Confirmation not received for data by " + str(client_num))
                    print("Will Retry")
                    continue

                # System has exited
                if kill_threads.is_set():
                    break

                data = None

def getClientNum(addr):
    return addr[1]

def receive_one_msg(connection, addr):
    global kill_threads
    global client_receive_conditions
    global client_socks

    client_num = 0
    receive_condition = client_receive_conditions[client_num]

    while True:

        if kill_threads.is_set():
            connection.close()
            return

        try:
            ready = select.select([connection], [], [], 2.0)
            if len(ready[0]) == 0:
                continue
            msg_len = connection.recv(2)
            msg_len = int.from_bytes(msg_len, "big")
            original_msg = connection.recv(msg_len)
            msg = pickle.loads(original_msg)

        except:
            print("Connection with " + str(addr) + " failed")
            client_socks[client_num] = None
            connection.close()
            return

        if msg[MSG_TYPE] == "HEARTBEAT":
            continue

        # CONFIRMATION MSG RECEIVED notify waiting thread
        elif msg[MSG_TYPE] == "CONFIRMATION":
            print("CONFIRMATION RECEIVED")
            receive_condition.acquire()
            receive_condition.notify()
            receive_condition.release()

        elif msg[MSG_TYPE] == "CLIENT_DETAILS":
            client_num = msg["CLIENT_NUM"]
            receive_condition = client_receive_conditions[client_num]

def receiveOneMessage(connection):
    msg_len = connection.recv(2)
    msg_len = int.from_bytes(msg_len, "big")
    msg = connection.recv(msg_len)
    return msg, pickle.loads(msg)

def start_receiving():
    global SERVER_PORT
    global listener
    global kill_listener_thread
    global kill_threads

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', SERVER_PORT))
    listener.listen()

    while not kill_threads.is_set():
        ready = select.select([listener], [], [], 2.0)
        if len(ready[0]) == 0:
            continue

        connection, addr = listener.accept()
        print("Incoming Connection from: " + socket.gethostbyaddr(addr[0])[0])
        # spawn a new thread to recestart_receiving()ive the message.
        r = threading.Thread(target=receive_one_msg,args=[connection,addr])
        r.start()
    listener.close()

def start_new_socket(client_num):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((client_ips[i], client_ports[i]))
        client_socks[client_num] = sock

    except:
        print("Connection To Client " + str(i) + " Failed")
        print("Marking node as down and will try to reconnect")
        client_socks.append(None)

def start_server():
    global client_socks
    global active_nodes
    global client_queues
    global client_thread_conditions
    global client_receive_conditions

    # signal.signal(signal.SIGINT, sigint_handler)

    for i in range(NUM_CLIENTS):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((client_ips[i], client_ports[i]))
            client_socks.append(sock)

        except:
            print("Connection To Client " + str(i) + " Failed")
            print("Marking node as down and will try to reconnect")
            client_socks.append(None)

        client_queues.append(queue.Queue())
        client_thread_conditions.append(threading.Condition())
        client_receive_conditions.append(threading.Condition())

        client_thread = threading.Thread(target=sendClientData, args=(i,))
        client_thread.start()

    threading.Thread(target=start_receiving).start()
    threading.Timer(WAKE_UP_THREAD_TIME_INTERVAL, wakeUpThreads).start()

def main():
    start_server()

    while True:
        data = input("Enter a Number\n")
        client_num = int(input("Enter Client Number\n"))
        pushData(client_num, data)

if __name__ == "__main__":
    main()
