import pygame
import sys
import logging
from logger import setup_logger
import socket
import queue
import select
import threading

HEADER = 64
PORT = 50009
FORMAT = 'UTF-8'
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)

# Initialize Pygame
setup_logger()

# Screen dimensions
WIDTH, HEIGHT = 800, 70
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

typing = False
text = ''
chat_log = []


class ChatLog:
    
    def __init__(self):
        self.history = []
        self.__lock = threading.Lock()
    
    def add(self, msg):
        with self.__lock:
            self.history.append(msg)

    def remove(self, index):
        with self.__lock:
            del self.history[index]
            
    def get_last(self, amount):
        with self.__lock:
            return self.history[-amount:]

    def get_copy(self):
        with self.__lock:
            return self.history.copy()


class ServerConnection:
    
    def __init__(self, 
                conn,
                game_queue,
                network_queue,
                chat_log):
        

        self.conn = conn
        self.game_queue = game_queue
        self.network_queue = network_queue
        self.chat_log = chat_log
        self.format = 'UTF-8'
        self.header = 64 
        
    def send(self, msg):
        msg_length = len(msg)
        send_length = str(msg_length).encode(self.format)
        send_length += b' ' * (self.header - len(send_length))
        self.conn.send(send_length)
        self.conn.send(msg.encode(self.format))
        logging.info(f"Message Sent '{msg}' To server")
        
    def run(self):
        while True:
            readable, writeable, exception = select.select([self.conn], [self.conn], [])
            if readable:
                msg_length = self.conn.recv(self.header).decode(self.format)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.conn.recv(msg_length).decode(self.format)
                    self.game_queue.put({'type': 'Message', 'msg': msg})
                    logging.info(f"Message Recieved'{msg}' From Server")
            
            if writeable:
                if not self.network_queue.empty():
                    item = self.network_queue.get()
                    if item['type'] == 'Message':
                        self.send(item['msg'])
                        
                        

    @classmethod
    def setup(cls, game_queue, network_queue, chat_log):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        network_client = cls(client, game_queue, network_queue, chat_log)
        thread = threading.Thread(target=network_client.run)
        thread.start()



class GameClient:
    def __init__(self, server, port):
        pygame.init()
        pygame.display.set_caption("Pygame Chat Client")
        

        # what we show
        self.screen = pygame.display.set_mode((1280, 960))
        self.font = pygame.font.Font('./src/client/content/fonts/Maplestory Bold.ttf', 20)

        self.network_queue = queue.Queue()
        self.game_queue = queue.Queue()
        threading.Thread(target=ServerConnection.setup, args=(self.game_queue, self.network_queue, )).start()
        
        # what we render on
        self.display = pygame.Surface((1280, 960))
        self.clock = pygame.time.Clock()
        
        self.input_box = pygame.Rect(50, HEIGHT - 50, 700, 40)
        self.text = ''
        self.typing = False
        
    def draw_text(self):
        pygame.draw.rect(self.display, BLACK, self.input_box)
        pygame.draw.rect(self.display, GRAY if typing else WHITE, self.input_box, 2)
        screen_text = self.font.render(self.text, True, WHITE)
        self.display.blit(screen_text, (self.input_box.x + 5, self.input_box.y + 5))

    def run(self):
        
        while True:
            self.display.fill((0, 0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quiting the Game.")
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    logging.debug(f"Mouse clicked at {event.pos}")
                    # If the user clicked on the input_box rect.
                    if self.input_box.collidepoint(event.pos):
                        logging.debug("Mouse Has collided with the input box")
                        self.typing = not self.typing
                    else:
                        logging.debug("Mouse has not collided with the input box")
                        self.typing = False

                if event.type == pygame.KEYDOWN:
                    if self.typing:
                        if event.key == pygame.K_RETURN:
                            self.network_queue.put({'type': 'Message', 'msg': self.text})
                            self.text = ''
                    
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode
                    else:
                        pass
                    
            self.draw_text()       
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    GameClient(SERVER, PORT).run()