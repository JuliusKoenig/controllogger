import dataclasses
import json
from pathlib import Path


@dataclasses.dataclass
class BaseDataclass:
    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, Path):
                return str(o)
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            if isinstance(o, object):
                return str(o)
            return super().default(o)

    def dict(self, exclude_none: bool = False) -> dict[str, any]:
        self_dict = dataclasses.asdict(self)

        # remove None values
        new_self_dict = {}
        if exclude_none:
            for key, value in self_dict.items():
                if value is None:
                    continue
                new_self_dict[key] = value
            self_dict = new_self_dict
        return self_dict

    def json(self, indent: int) -> str:
        self_dict = self.dict()

        self_json = json.dumps(self_dict, indent=indent, cls=self.JSONEncoder)

        return self_json
