from dataclasses import dataclass
from typing import Optional
from enum import Enum

class ApiKeyType(Enum):
    API_KEY_TYPE__UNDEFINED = 0
    # ApiKey for serving.Only gives access to query data.
    API_KEY_TYPE__SERVING = 1
    #/ ApiKey for serving and indexing.Gives access to both query and index data.
    API_KEY_TYPE__SERVING_INDEXING = 2

class ApiKeyStatus(Enum):
    UNKNOWN = 0
    ENABLED = 1
    DISABLED = 2
    DELETED = 3

