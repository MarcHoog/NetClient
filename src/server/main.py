import socket
import threading
import logging
from logger import setup_logger
import select
import queue

class ClientConnection:
    
    def __init__(self, 
                 conn, 
                 addr, 
                 master_queue):
        
        self.conn = conn
        self.addr = addr
        self.hostname = addr[0]
        self.port = addr[1]
        self.master_queue = master_queue
        self.queue = queue.Queue()
        self.format = 'UTF-8'
        self.header = 64 
        
        self.notify_new_client()
        
    def notify_new_client(self):
        logging.info(f'New Client: Connected by {self.addr[0]}:{self.addr[1]}')
        self.master_queue.put({'type': 'NewClient', 'addr': self.addr, 'client_queue': self.queue})
        
    def send(self, msg):
        msg_length = len(msg)
        send_length = str(msg_length).encode(self.format)
        send_length += b' ' * (self.header - len(send_length))
        self.conn.send(send_length)
        self.conn.send(msg.encode(self.format))
        logging.info(f"Message Sent '{msg}' To {self.addr[0]}:{self.addr[1]}")
        
    def run(self):
        while True:
            readable, writeable, exception = select.select([self.conn], [self.conn], [])
            if readable:
                msg_length = self.conn.recv(self.header).decode(self.format)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.conn.recv(msg_length).decode(self.format)
                    self.master_queue.put({'type': 'Message', 'msg': msg})
                    logging.info(f"Message Recieved'{msg}' From {self.addr[0]}:{self.addr[1]}")
            
            if writeable:
                if not self.queue.empty():
                    item = self.queue.get()
                    if item['type'] == 'Message':
                        self.send(item['msg'])

    @classmethod
    def setup(cls, conn, addr, master_queue):
        client = cls(conn, addr, master_queue)
        thread = threading.Thread(target=client.run)
        thread.start()
        
class Server:
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
        self.run()

    def setup_listening_thread(self):
        """
        Sets up a listening thread that listens for incomming connections
        """
        thread = threading.Thread(target=self._listening_thread, args=())
        thread.start()
        return thread

    def _listening_thread(self):
        logging.info('listening thread has been started....')
        logging.info('Listening for Connections')

        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=ClientConnection.setup, args=(conn, addr, self.master_queue))
            thread.start()


    def run(self):
        while True:
            if not self.master_queue.empty():
                item = self.master_queue.get()
                if item['type'] == 'NewClient':
                    
                    self.clients[f'{item["addr"][0]}:{item["addr"][1]}'] = item['client_queue']
                    
                    logging.debug(f'New Client: {item["addr"][0]}:{item["addr"][1]} has been added to the server broadcast list')
                
                elif item['type'] == 'Message':
                    for client in self.clients:
                        logging.debug(f'Message Broadcasted to {client}')
                        self.clients[client].put({'type': 'Message', 'msg': item['msg']})




if __name__ == "__main__":
    
    setup_logger()
    Server("127.0.0.1", 50009)