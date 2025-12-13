from flask import Flask, render_template, request
from config import Config
from hafas import HafasAPI, Stop
import threading
import urllib.request



class Screen:


    def __init__(self):
        self._config = Config()
        self._thread = None

        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'render_screen', self.render_screen)
        self.app.add_url_rule('/_shutdown', '_shutdown', self._shutdown, methods=['POST'])
        self.app.add_url_rule('/_update', '_update', self._update, methods=['POST'])

        # Initialize HAFAS API and selected stop
        self._hafas = HafasAPI()
        self._selected_stop: Stop = None if not self._config.get("stop_name") else self._hafas.get_stop(self._config.get("stop_name"))
        if self._selected_stop:
            self._hafas.set_selected_stop(self._selected_stop)


    def render_screen(self):

        if not ((self._config.get("stop_name") and self._selected_stop)):
            return render_template('no_stop.html')
        
        departures = self._hafas.get_departures(self._config.get("max_departures"))
        return render_template('screen.html', stop=self._selected_stop, departures=departures)


    def _shutdown(self): 
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running the Werkzeug Server')
        func()
        return 'shutting down'


    def _update(self):
        self._config.load_config()
        self._selected_stop = self._hafas.get_stop(self._config.get("stop_name"))
        return 'updated'


    def start(self, port: int = 8080, block: bool = False):
        if self.is_running():
            return

        print("Starting server...")

        run_kwargs = {'host': '127.0.0.1', 'port': 8080, 'debug': False, 'use_reloader': False}
        self._thread = threading.Thread(target=self.app.run, kwargs=run_kwargs, daemon=True)
        self._thread.start()

        if block:
            try:
                self._thread.join()
            except KeyboardInterrupt:
                self.stop()


    def stop(self):
        
        if not self.is_running():
            return

        print("Stopping server...")

        try:
            req = urllib.request.Request('http://127.0.0.1:8080/_shutdown', method='POST')
            with urllib.request.urlopen(req, timeout=2):
                pass
        except Exception:
            # ignore any error during shutdown request
            pass

        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()


if __name__ == '__main__':
    s = Screen()
    s.start(block=True)
