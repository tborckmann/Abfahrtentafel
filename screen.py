from flask import Flask, render_template, request
from config import Config
import threading
import urllib.request


class Screen:
    app = Flask(__name__)
    PORT = Config().get("port") or 8080


    def __init__(self):
        self.config = Config()
        self._thread = None

    @app.route('/')
    def render_screen():

        # TODO: Render website for departure board

        return render_template('no_stop.html')

    @app.route('/_shutdown', methods=['POST'])
    def _shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running the Werkzeug Server')
        func()
        return 'shutting down'

    def start(self, port: int = None, block: bool = False):
        if self.is_running():
            return

        print("Starting server...")

        if port is None:
            port = self.PORT

        run_kwargs = {'host': '127.0.0.1', 'port': port, 'debug': False, 'use_reloader': False}
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
            req = urllib.request.Request(f'http://127.0.0.1:{self.PORT}/_shutdown', method='POST')
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
