import threading
condition = threading.Condition()

def func1():
    global condition
    with condition:
        print("got lock1")
        condition.wait()
        print("here1")

def func2():
    global condition
    condition.acquire()
    condition.notify()
    print("got lock2")
    with condition.wait():
        print("here2")
        return

threading.Thread(target=func1).start()
