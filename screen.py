from flask import Flask, render_template, request
from config import Config
from hafas import HafasAPI, Stop
from shared import ConnectionError, RequestException, ConfigError
import threading
import urllib.request



class Screen:


    def __init__(self):
        self._config = Config()
        self._thread = None
        self._selected_stop: Stop = None

        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'render_screen', self.render_screen)
        self.app.add_url_rule('/_shutdown', '_shutdown', self._shutdown, methods=['POST'])
        self.app.add_url_rule('/_update', '_fetch_stop', self._fetch_stop, methods=['POST'])

        
        self._hafas = HafasAPI()
        try:
            self.fetch_stop()   # Ignore Exceptions on first fetch
        except:
            print("Couldnt fetch stop on init")


    def _fetch_stop(self):

        self._config.load_config()
        if not self._config.get("stop_name"):
            raise ConfigError("stop_name", None)
        
        self._selected_stop = self._hafas.get_stop(self._config.get("stop_name"))
        self._hafas.set_selected_stop(self._selected_stop)
        return "updated"

    def render_screen(self):
        
        try:
            if not self._selected_stop:
                self._fetch_stop()
            
            departures = self._hafas.get_departures(self._config.get("max_departures"))
            return render_template("screen.html", stop_name=self._selected_stop.display_name, departures=departures)
        except ConfigError as confe:
            print("Stop not specified" + str(confe.message))
            return render_template("error.html", error="No Stop specified", msg="Edit config to select a stop and send update request")
        except ConnectionError as ce:
            print("Not connected: " + str(ce.message))
            return render_template("error.html", error="No Connection", msg = "Try connecting to the internet")
        except RequestException as re:
            match re.status_code:
                case 403:
                    return render_template("error.html", error="Request error: Access forbidden", msg="Access was not permitted (Error 403)")
                case 404:
                    return render_template("error.html", error="Request error: Wrong URL", msg="API could not be found (Error 404)")
                case 429:
                    return render_template("error.html", error="Request error: Rate limited", msg="Too many requests were sent (Error 429)")
                case _:
                    return render_template("error.html", error="Request error", msg=f"There was an error (Error {re.status_code})")


    def _shutdown(self): 
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running the Werkzeug Server')
        func()

        return 'shutting down'


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

        if self._thread is not threading.current_thread:
            self._thread.join(timeout=2)
            self._thread = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()


if __name__ == '__main__':
    s = Screen()
    s.start(block=True)
