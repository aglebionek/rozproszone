from typing import Any

class Response:
    def __init__(self, command: str = "", data: dict[str, Any] = {}, error = "") -> None:
        self.command = command
        self.data = data
        self.error = error
        
    def __str__(self) -> str:
        return f"Command: {self.command}\nData: {self.data}\nError: {self.error}"