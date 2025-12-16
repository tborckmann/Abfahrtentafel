import threading
shutdown_event = threading.Event()


class ConnectionError(Exception):
    
    def __init__(self, message: str, body: str):
        self.message = message
        self.body = body
        super().__init__(message)


class RequestException(Exception):
    
    def __init__(self, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)