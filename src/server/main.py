import socket
import threading
import logging
from logger import setup_logger
import select
import queue


# Python Non blocking Terminal idea 1 
# Put this all on git
# Using Queue's to send messages to the server
# There is a main thread that listens from messages
# There is a thread and a queue that sends messages for each client 
# https://docs.python.org/3/library/queue.html#queue-objects
# https://docs.python.org/3/library/select.html


#                                         / - [sending Queu][Client1]
#[Client0] -> [listening Queue][Server]  - 
#                                        \ - [sending Queu][Client2]

NEW_CLIENT = 0
NEW_MESSAGE = 1
DISCONNECT = 2

if __name__ == "__main__":
    
    setup_logger()
    
    HOST = '127.0.0.1'
    PROT = 50009
    HEADER = 64
    FORMAT = 'UTF-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PROT))

    def client_thread(conn, addr, client_queue, master_queue):
        connected = True
        logging.info(f'Connected by {addr[0]}:{addr[1]}')
        while connected:
            readable, writeable, exception = select.select([conn], [], [])
            if readable:
                msg_length = conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    logging.info(f"Message recieved : '{msg}' From {addr[0]}:{addr[1]}")
                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                        
            
        conn.close()
    
    def listing_thread(master_queue):
        server.listen()
        logging.info('listening thread has been started....')
        logging.info('Listening for Connections')
        
        while True:
            conn, addr = server.accept()
            logging.info('Connection Accepted')
            client_queue = queue.Queue()
            master_queue.put((NEW_CLIENT, (conn, addr, client_queue)))
            thread = threading.Thread(target=client_thread, args=(conn, addr, client_queue, master_queue))
            thread.start()
            logging.info(f'Active threads: {threading.active_count() - 1}')

    def setup_server():
        master_queue = queue.Queue()
        thread = threading.Thread(target=listing_thread, args=(master_queue, ))
        thread.start()
        logging.info(f'Active threads: {threading.active_count() - 1}')
        return master_queue

    def start():
        master_queue = setup_server()
        clients = {}        
        
        while True:
            if not master_queue.empty():
                item = master_queue.get()
                if item[0] == NEW_CLIENT:
                    logging.info(f'New Client: {item[1][1][0]}:{item[1][1][1]} added to main thread')
                    clients[f'{item[1][1][0]}:{item[1][1][1]}'] = item[1][2]
            else:
                pass



    start()