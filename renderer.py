import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from screen import Screen
import time, threading, urllib.request

class Renderer:

    driver: webdriver = None
    screen: Screen = None

    def __init__(self, screen: Screen = Screen()):

        self.screen = screen
        if not screen.is_running():
            screen.start()

        self._thread = None

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--window-size=800,480')

        self.driver = webdriver.Chrome(options=options)
        self.start()
    
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

        self.driver.quit()
        self.screen.stop()

        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def render(self, url: str):
        self.driver.get(url)
        print(f"Opened {url}")

        while True:
            time.sleep(5)

            try:
                req = urllib.request.Request(url)
                urllib.request.urlopen(req, timeout=2)
            except Exception as e:
                print("Web server not running, stopping renderer...")
                self.stop()
                return

            self.driver.refresh()
            self.driver.save_screenshot("screenshot.png")
            print("Screenshot saved")


if __name__ == '__main__':
    screen = Screen()
    screen.start()

    renderer = Renderer(screen)

    