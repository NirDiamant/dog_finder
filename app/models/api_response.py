from typing import Any
from pydantic import BaseModel

class APIResponse(BaseModel):
    status_code: int = 200
    message: str = "OK"
    data: Any = None
    meta: dict = {}

    def to_dict(self) -> dict:
        return {
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data,
            "meta": self.meta
        }