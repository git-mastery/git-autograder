from json import JSONEncoder
from typing import Any
from datetime import datetime


class Encoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.timestamp()
        return super().default(o)
