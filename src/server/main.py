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

class Server():
    def __init__(self, host, port):
        self.clients = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.format = 'UTF-8'
        self.header = 64 

        self.server.bind((self.host, self.port))
        self.master_queue = queue.Queue()

        self.setup_listening_thread()
        self._master_thread()

    def setup_listening_thread(self):
        """
        Sets up a listening thread that listens for incomming connections
        """
        thread = threading.Thread(target=self._listening_thread, args=())
        thread.start()
        logging.info(f'Active threads: {threading.active_count() - 1}')
        return thread

    def _listening_thread(self):
        logging.info('listening thread has been started....')
        logging.info('Listening for Connections')

        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            client_queue = queue.Queue()
            self.clients[addr] = client_queue
            thread = threading.Thread(target=self._client_thread, args=(conn, addr, client_queue))
            thread.start()


    def _client_thread(self, conn, addr, client_queue):
        connected = True
        logging.info(f'Connected by {addr[0]}:{addr[1]}')
        while connected:
            readable, writeable, exception = select.select([conn], [], [])
            if readable:
                msg_length = conn.recv(self.header).decode(self.format)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(self.format)
                    logging.info(f"Message recieved : '{msg}' From {addr[0]}:{addr[1]}")
            if not client_queue.empty():
                message = client_queue.get()
                conn.send(message.encode(self.format))
                logging.info(f"Message sent: '{message}' to {addr[0]}:{addr[1]}")

        conn.close()


    def _master_thread(self):
        while True:
            if not self.master_queue.empty():
                item = self.master_queue.get()
                if item['type'] == 'NewClient':
                    logging.info(f'New Client: {item["addr"][0]}:{item["addr"][1]} added to main thread')
                    self.clients[{item["addr"][0]}:{item["addr"][1]}] = item['client_queue']
            else:
                pass

if __name__ == "__main__":
    
    setup_logger()
    Server("127.0.0.1", 50009)