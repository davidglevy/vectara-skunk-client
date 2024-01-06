from dataclasses import dataclass
from typing import Optional
from enum import Enum

class StatusCode(Enum):



    OK = 0
    FAILURE = 1
    # gRPC Codes - ---------------------------------------------------------------
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    UNIMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15
    UNAUTHENTICATED = 16

    # HTTP Codes - ---------------------------------------------------------------
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNSUPPORTED_MEDIA_TYPE = 415
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503
    INSUFFICIENT_STORAGE = 507

    UNPARSEABLE_RESPONSE = 1000

    # General Failures - ----------------------------------------------------------
    DISABLED_CUSTOMER = 1100
    INVALID_CUSTOMER_ID = 1101
    DISABLED_CORPUS = 1102
    INVALID_CORPUS_ID = 1103
    DISABLED_API_KEY = 1104
    EXPIRED_API_KEY = 1105
    INVALID_API_KEY = 1106

    # Serving Query - ------------------------------------------------------------
    QRY__DISABLED_CORPUS = 1500
    QRY__DOCUMENT_DB_FAILURE = 1505
    QRY__ENCODER_FAILURE = 1510
    QRY__INTERRUPTED = 1515
    QRY__INVALID_CORPUS = 1520
    QRY__INVALID_START = 1525
    QRY__INVALID_NUM_RESULTS = 1530
    QRY__MISSING_QUERY = 1535
    QRY__MISSING_CORPUS = 1540
    QRY__TIMEOUT = 1545
    QRY__TOO_MANY_CORPORA = 1550
    QRY__TOO_MANY_QUERIES = 1555
    QRY__VECTOR_INDEX_FAILURE = 1560
    QRY__INVALID_DIMENSION = 1565
    QRY__INVALID_CLIENTKEY = 1570
    QRY__DECRYPTION_FAILURE = 1575
    QRY__INVALID_RERANKER = 1580
    QRY__PARTIAL_RERANK = 1585
    QRY__RERANK_FAILURE = 1590
    QRY__TOO_MANY_RESULT_ROWS = 1595

    # Connection specs - ---------------------------------------------------------
    CX_SPECS__INVALID_JSON = 2000
    CX_SPECS__UNREGISTERED_TYPE = 2005
    CX_SPECS__MISSING_SPEC = 2010
    CX_SPECS__MISSING_TYPE = 2011
    CX_SPECS__UNPARSEABLE_SPEC = 2015

    # Admin Service - ------------------------------------------------------------
    ADM__INVALID_CUSTOMER_ID = 2500
    ADM__INVALID_CORPUS_ID = 2501
    ADM__INVALID_ENCODER_ID = 2502
    ADM__INVALID_ROLE_ID = 2503
    ADM__ROLE_ALREADY_EXISTS = 2504
    ADM__ONLY_ONE_OWNER_SUPPORTED = 2505
    ADM__INVALID_PERMISSION = 2506
    ADM__ROLECREATION_FAILURE = 2507
    ADM__USER_EMAIL_NOT_AVAIALBLE = 2508
    ADM__USERNAME_NOT_AVAILABLE = 2509

    ADM__SIGNUP_MISSING_NAME = 2510
    ADM__SIGNUP_MISSING_ORG = 2511
    ADM__SIGNUP_MISSING_EMAIL = 2512
    ADM__SIGNUP_MISSING_PAYMENT = 2513
    ADM__SIGNUP_MISSING_PLAN = 2514
    ADM__SIGNUP_MISSING_PASSWORD = 2515

    ADM__SIGNUP_INVALID_NAME = 2516
    ADM__SIGNUP_INVALID_ORG = 2517
    ADM__SIGNUP_INVALID_EMAIL = 2518
    ADM__SIGNUP_INVALID_PAYMENT = 2519
    ADM__SIGNUP_INVALID_PLAN = 2520
    ADM__SIGNUP_INVALID_PASSWORD = 2521
    ADM__SIGNUP_INVALID_ACCOUNT_ALIAS = 2530
    ADM__SIGNUP_INVALID_EMAIL_VALIDATION_CODE = 2531

    ADM__CUST_MARK_DELETE_FAILED = 2522
    ADM__CUST_FAISS_DEALLOC_FAILED = 2523

    ADM__CORPUS_LIMIT_REACHED = 2524

    ADM__STRIPE_CARD_DECLINED = 2525
    ADM__STRIPE_PROCESSING_ERROR = 2526

    ADM__EMAIL_VALIDATION_REQUEST_NOT_FOUND = 2540
    ADM__EMAIL_NOT_VALIDATED = 2541

    # Schema Services - ----------------------------------------------------------
    SCM__MISCONFIGURED_CONNECTION = 3000

    # Druid Errors
    DRUID_READ_FAILURE = 3500
    DRUID_INVALID_DATA = 3501
    DRUID_NO_DATA = 3502

    # StatDB Errors
    STATS_DB_READ_FAILURE = 3550

    # Vector Database - ----------------------------------------------------------

    VDB__TEXT_READ_FAILURE = 4000

    # Index rebuild codes - -----------------------------------------------------
    REBUILD__LOW_RECALL = 4500
    REBUILD__INDEX_UPLOAD_FAILURE = 4505
    REBUILD__UPDATE_JOURNAL_FAILURE = 4510
    REBUILD__UPDATE_FAISSPARAMS_FAILURE = 4515
    REBUILD__NO_DATA = 4520
    REBUILD__EVALUATION = 4525

    # Indexing - -----------------------------------------------------------------
    IDX__TRANSIENT_PARTIAL_DELETION_FAILURE = 5000
    IDX__PERMANENT_PARTIAL_DELETION_FAILURE = 5001


@dataclass
class Status:
    """
    Including these as optional because file upload response has this as an empty object on success
    """
    code: Optional[str | StatusCode]
    #code_enum: Optional[StatusCode]
    statusDetail: Optional[str]
    cause: Optional[str]

    def __post_init__(self):
        """
        Hacky way to transform the str back into the enum value.
        """
        if isinstance(self.code, str):
            self.code = StatusCode[self.code]