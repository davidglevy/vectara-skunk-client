from enum import Enum

def _custom_asdict_factory(data):

    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.name
        return obj

    return dict((k, convert_value(v)) for k, v in data)