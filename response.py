from typing import Any

class Response:
    def __init__(self, success: bool, data: dict[str, Any] = {}, error = "") -> None:
        self.success = success
        self.data = data
        self.error = error
        
    def __str__(self) -> str:
        return f"Success: {self.success}\nData: {self.data}\nError: {self.error}"