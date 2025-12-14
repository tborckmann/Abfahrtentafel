import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from screen import Screen
from config import Config
from shared import shutdown_event
import time, threading, urllib.request

class Renderer:

    driver: webdriver = None
    screen: Screen = None

    

    def __init__(self, screen: Screen = Screen(), headless: bool = True):

        self.screen = screen
        if not screen.is_running():
            screen.start()

        self._thread = None

        self._config = Config()
        self.REFRESH_INTERVAL = self._config.get("refresh_interval")

        options = Options()
        if headless: options.add_argument('--headless')
        options.add_argument('--window-size=800,480')

        self.driver = webdriver.Chrome(options=options)
    
    def start(self):
        if self.is_running():
            return
        
        print("Starting renderer...")

        self._thread = threading.Thread(target=self.render, args=(f"http://localhost:8080/",))
        self._thread.start()

    def stop(self):
        
        if not self.is_running():
            return

        print("Stopping renderer...")

        try:
            self.driver.quit()
        except Exception:
            pass

        if self.screen.is_running(): 
            self.screen.stop()

        if self._thread is not threading.current_thread():
            self._thread.join()
            self._thread = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def render(self, url: str):
        self.driver.get(url)
        print(f"Opened {url}")

        while True:

            if shutdown_event.is_set():
                self.stop()
                return

            try:
                req = urllib.request.Request(url)
                urllib.request.urlopen(req, timeout=2)
            except Exception as e:
                print("Web server not running, stopping renderer...")
                shutdown_event.set()
                continue

            try:
                self.driver.refresh()
                self.driver.save_screenshot("screenshot.png")
                print("Screenshot saved")
            except Exception as e:
                print("Browser closed, stopping renderer...")
                shutdown_event.set()
                continue
            

            shutdown_event.wait(self.REFRESH_INTERVAL)



if __name__ == '__main__':
    screen = Screen()
    screen.start()

    renderer = Renderer(screen, False)
    renderer.start()

    try:
        while not shutdown_event.is_set():
            time.sleep(0.5)
        
        if shutdown_event.is_set():
            renderer.stop()
            screen.stop()
    except KeyboardInterrupt:
        shutdown_event.set()
    