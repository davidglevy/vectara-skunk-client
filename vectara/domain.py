import logging
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from vectara.status import Status
from vectara.enums import ApiKeyStatus, ApiKeyType

"""
Definitions taken from admin.proto in platform.
"""

class FilterAttributeType(Enum):
    FILTER_ATTRIBUTE_TYPE__UNDEFINED = 0
    FILTER_ATTRIBUTE_TYPE__INTEGER = 5
    FILTER_ATTRIBUTE_TYPE__INTEGER_LIST = 10
    FILTER_ATTRIBUTE_TYPE__REAL = 15
    FILTER_ATTRIBUTE_TYPE__REAL_LIST = 20
    FILTER_ATTRIBUTE_TYPE__TEXT = 25
    FILTER_ATTRIBUTE_TYPE__TEXT_LIST = 30

class FilterAttributeLevel(Enum):
    FILTER_ATTRIBUTE_LEVEL__UNDEFINED = 0
    FILTER_ATTRIBUTE_LEVEL__DOCUMENT = 5 # Document - level attribute
    FILTER_ATTRIBUTE_LEVEL__DOCUMENT_PART = 10 # Part - level attribute

@dataclass
class Dimension:
    name: str
    description: str
    serving_default: str
    indexing_default: str

@dataclass
class FilterAttribute:
    name: str
    description: str
    indexed: bool
    type: FilterAttributeType
    level: FilterAttributeLevel

@dataclass
class Corpus:
    id: int
    name: str
    description: str
    dtProvision: str
    enabled: bool
    swapQenc: bool
    swapIenc: bool
    textless: bool
    encrypted: bool
    encoderId: str
    metadataMaxBytes: int
    faissIndexType: str
    customDimensions: List[Dimension]
    filterAttributes: List[FilterAttribute]


@dataclass
class ListCorpusResponse:

    corpus: List[Corpus]


@dataclass
class ReadCorpusRequest:
    corpus_id: List[int]
    read_basic_info: bool
    read_size: bool
    read_recall: bool
    read_api_keys: bool
    read_custom_dimensions: bool
    read_filter_attributes: bool


@dataclass
class CorpusSize:
    epochSecs: str # Different from proto: epoch_secs : int
    size: str # Different from proto: size : int

@dataclass
class CorpusRecall:
    epochSecs: str
    recall: str
    sampleSize: str

@dataclass
class ApiKey:
    id: str
    description: str
    keyType: str | ApiKeyType
    enabled: bool
    tsStart: str
    tsEnd: Optional[str]
    status: str | ApiKeyStatus

    def __post_init__(self):
        """
        Hacky way to transform the str back into the enum value.
        """
        if self.keyType and isinstance(self.keyType, str):
            self.keyType = ApiKeyType[self.keyType]
        if self.status and isinstance(self.status, str):
            self.status = ApiKeyStatus[self.status]


@dataclass
class CorpusInfo:
    corpus: Corpus
    corpusStatus: Status # Different from proto: corpus_status
    size: CorpusSize
    sizeStatus : Status # Different from proto: size_status
    recall: Optional[CorpusRecall]
    recallStatus: Optional[Status]
    apiKey: List[ApiKey]


@dataclass
class ReadCorpusResponse:
    corpora: List[CorpusInfo]

