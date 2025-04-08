from datetime import datetime
from json import JSONEncoder
from typing import Any


class Encoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.timestamp()
        return super().default(o)
