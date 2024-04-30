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

class ApiKeySort(Enum):
    START_TS = 0,
    END_TS = 1,
    DESCRIPTION = 2,
    KEY_TYPE = 3,
    STATUS = 4

class SortDirection(Enum):
    ASC = 0,
    DESC = 1

class UsageMetric(Enum):
    METRICTYPE__NONE = 0,
    METRICTYPE__INDEXING = 1,
    METRICTYPE__SERVING = 2





