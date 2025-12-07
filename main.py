from renderer import Renderer
from screen import Screen
from config import Config
import threading, time

if __name__ == '__main__':
    screen = Screen()
    screen.start()
    
    renderer = Renderer(screen)