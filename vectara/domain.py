import logging
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from vectara.status import Status
from vectara.enums import ApiKeyStatus, ApiKeyType

from dataclasses import dataclass

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
    FILTER_ATTRIBUTE_TYPE__BOOLEAN = 35


class FilterAttributeLevel(Enum):
    FILTER_ATTRIBUTE_LEVEL__UNDEFINED = 0
    FILTER_ATTRIBUTE_LEVEL__DOCUMENT = 5  # Document - level attribute
    FILTER_ATTRIBUTE_LEVEL__DOCUMENT_PART = 10  # Part - level attribute


@dataclass
class Dimension:
    name: str
    description: str
    serving_default: str
    indexing_default: str


@dataclass
class FilterAttribute:
    name: str
    description: Optional[str]
    indexed: bool
    type: str | FilterAttributeType
    level: str | FilterAttributeLevel

    def __post_init__(self):
        """
        Hacky way to transform the str back into the enum value.
        """
        if self.type and isinstance(self.type, str):
            self.type = FilterAttributeType[self.type]
        if self.level and isinstance(self.level, str):
            self.level = FilterAttributeLevel[self.level]


@dataclass
class Corpus:
    id: Optional[int]
    name: str
    description: Optional[str]
    dtProvision: Optional[str]
    enabled: Optional[bool]
    swapQenc: Optional[bool]
    swapIenc: Optional[bool]
    textless: Optional[bool]
    encrypted: Optional[bool]
    encoderId: Optional[str]
    metadataMaxBytes: Optional[int]
    faissIndexType: Optional[str]
    customDimensions: Optional[List[Dimension]]
    filterAttributes: Optional[List[FilterAttribute]]


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
    epochSecs: str  # Different from proto: epoch_secs : int
    size: str  # Different from proto: size : int


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
    corpusStatus: Status  # Different from proto: corpus_status
    size: CorpusSize
    sizeStatus: Status  # Different from proto: size_status
    recall: Optional[CorpusRecall]
    recallStatus: Optional[Status]
    apiKey: List[ApiKey]
    # Test from here
    apiKeyStatus: Optional[Status]
    customDimension: List[Dimension]
    customDimensionStatus: Optional[Status]
    filterAttribute: List[FilterAttribute]
    filterAttributeStatus: Optional[Status]


@dataclass
class ReadCorpusResponse:
    corpora: List[CorpusInfo]


@dataclass
class CreateCorpusRequest:
    corpus: Corpus


@dataclass
class CreateCorpusResponse:
    corpusId: int
    status: Status


@dataclass
class DeleteCorpusRequest:
    customerId: int
    corpusId: int


@dataclass
class DeleteCorpusResponse:
    status: Status


@dataclass
class StorageQuota:
    numChars: str
    numMetadataChars: str


@dataclass
class CustomDimension:
    name: str
    value: float


@dataclass
class Section:
    id: Optional[int]
    title: Optional[str]
    text: Optional[str]
    metadataJson: Optional[str]
    customDims: Optional[List[CustomDimension]]
    section: Optional[List['Section']]


@dataclass
class Document:
    documentId: str
    title: Optional[str]
    description: Optional[str]
    metadata_json: Optional[str]
    customDims: Optional[List[CustomDimension]]
    section: List[Section]


@dataclass
class UploadDocumentResponseInner:
    status: Optional[Status]
    quotaConsumed: StorageQuota

    def __post_init__(self):
        """
        Funky behavior to clear the status if it doesn't have a code
        """
        if not self.status.code:
            self.__setattr__("status", None)


@dataclass
class UploadDocumentResponse:
    response: UploadDocumentResponseInner
    document: Optional[Document]


@dataclass
class QueryContextConfig:
    charsBefore: Optional[int]
    charsAfter: Optional[int]
    sentencesBefore: Optional[int]
    sentencesAfter: Optional[int]
    startTag: Optional[str]
    endTag: Optional[str]


@dataclass
class QueryDim:
    name: str
    weight: int


class Semantics(Enum):
    DEFAULT = 0
    QUERY = 1
    RESPONSE = 2


@dataclass
class LinearInterpolation:
    _lambda: Optional[float]  # Unfortunately Python dataclass attributes cannot be reserved words.


@dataclass
class CorpusKey:
    corpusId: int
    customerId: Optional[int]
    semantics: Optional[str | Semantics]
    dim: Optional[List[CustomDimension]]
    metadataFilter: Optional[str]
    lexicalInterpolationConfig: Optional[LinearInterpolation]

    def __post_init__(self):
        """
        Hacky way to transform the str back into the enum value.
        """
        if self.semantics and isinstance(self.semantics, str):
            self.semantics = Semantics[self.semantics]


@dataclass
class MMRConfig:
    """
    Intuitively, this bias controls how much the reranker should favor
    diversity over relevance. A bias of 1 means that relevance is not
    considered at all, while a bias of 0 means that diversity is not
    considered. A score of 0.8 means that diversity counts for 80% of the
    score, and relevance for 20%.

    The bias is defined as (1 - lambda), where lambda is defined as in
    the original paper, "The Use of MMR, Diversity-Based Reranking for
    Reordering Documents and Producing Summaries" by Carbonell and Goldstein,
    1998.
    """
    diversityBias = float


@dataclass
class RerankingConfig:
    rerankerId: int
    mmrConfig: Optional[MMRConfig]


@dataclass
class Summarizer:
    summarizerPromptName: str
    promptText: Optional[str]
    responseLang: str
    maxSummarizedResults: int


@dataclass
class QueryBody:
    query: str
    start: Optional[int]
    numResults: Optional[int]
    contextConfig: Optional[QueryContextConfig]
    corpusKey: List[CorpusKey]
    rerankingConfig: Optional[RerankingConfig]
    summary: Optional[List[Summarizer]]


@dataclass
class BatchQueryRequest:
    query: List[QueryBody]


@dataclass
class Attribute:
    name: str
    value: str


@dataclass
class Response:
    text: str
    score: float
    metadata: List[Attribute]
    documentIndex: int
    corpusKey: CorpusKey
    resultOffset: int
    resultLength: int

@dataclass
class ResponseDocument:
    id: str
    metadata: List[Attribute]


@dataclass
class SummaryResponse:
    text: Optional[str]
    lang: str
    prompt: str
    status: List[Status]
    # Do we need to serialize "futureId"?

@dataclass
class ResponseSet:
    response: List[Response]
    status: List[Status]
    document: Optional[List[ResponseDocument]]
    summary: Optional[List[SummaryResponse]]

@dataclass
class PerformanceMetrics:
    queryEncodeMs: int
    retrievalMs: int
    userdataRetrievalMs: int
    rerankMs: int


@dataclass
class BatchQueryResponse:
    responseSet: Optional[List[ResponseSet]]
    status: List[Status]
    metrics: Optional[PerformanceMetrics]

@dataclass
class CoreDocumentPart:
    text: Optional[str]
    context: Optional[str]
    metadata_json: Optional[str]
    custom_dims: Optional[List[CustomDimension]]

@dataclass
class CoreDocument:
    """
    Something odd
    """
    document_id: str
    title: str
    metadata_json: Optional[str]
    section: Optional[List[CoreDocumentPart]]
    #default_part_context: Optional[str]
    custom_dims: Optional[List[CustomDimension]]

@dataclass
class IndexDocumentRequest:
    """
    See core_services.proto
    """
    customer_id: int
    corpus_id: int
    document: CoreDocument

@dataclass
class IndexDocumentResponse:
    """
    See core_services.proto
    """
    status: Status
    quotaConsumed: Optional[StorageQuota]

    def __post_init__(self):
        """
        Funky behavior to clear the status if it doesn't have a code
        """
        if not self.status.code:
            self.__setattr__("status", None)