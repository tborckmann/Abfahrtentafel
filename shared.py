import threading
shutdown_event = threading.Event()


class ConnectionError(Exception):
    
    def __init__(self, message: str = None):
        self.message = message
        super().__init__(self.message)


class RequestException(Exception):
    
    def __init__(self, status_code: int, message: str = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


from typing import Any
class ConfigError(Exception):

    def __init__(self, option_name: str, option_value: Any):
        self.option_name = optin_name
        self.option_value = option_value
        self.message = f"Value {self.option_value} invalid for option {self.option_name}"
        super().__init__(self.message)