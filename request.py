from typing import Any

class Request:
    def __init__(self, command: str = '', user: str = '', data: dict[str, Any] = {}) -> None:
        self.command = command
        self.user = user
        self.data = data
        
    def __str__(self) -> str:
        return f"User: {self.user}, Command: {self.command}\nData: {self.data}"