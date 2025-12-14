from renderer import Renderer
from screen import Screen
from config import Config
from shared import shutdown_event
import threading, time, sys

if __name__ == '__main__':

    screen = Screen()
    screen.start()

    renderer = Renderer(screen, False)
    renderer.start()

    try:
        while not shutdown_event.is_set():
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("KeyboardInterrupt received")
        shutdown_event.set()

    finally:
        screen.stop()
        renderer.stop()
        
        print("Main thread shutting down...")

        # Optional: allow renderer cleanup time
        time.sleep(0.5)
