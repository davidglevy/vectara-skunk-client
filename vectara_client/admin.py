from dataclasses import asdict
from vectara_client.domain import *
from vectara_client.enums import ApiKeyStatus, ApiKeyType, ApiKeySort, SortDirection
from dacite import from_dict
from typing import List, TypeVar, Union
from vectara_client.status import StatusCode
from vectara_client.util import _custom_asdict_factory, RequestUtil
from datetime import datetime, timezone
import logging

T = TypeVar("T")

class AdminService():

    def __init__(self, request_util: RequestUtil, customer_id: int):
        self.logger = logging.getLogger(__class__.__name__)
        self.request_util = request_util
        self.customer_id = customer_id

    def list_corpora(self, filter: str = None, numResults: int = None, pageKey: int = None) -> List[Corpus]:
        payload = {}
        if filter:
            payload['filter'] = filter
        if numResults:
            payload['numResults'] = numResults
        if pageKey:
            payload['pageKey'] = pageKey

        response = self.request_util.request("list-corpora", payload, ListCorpusResponse)
        response.corpus.sort(key=lambda x: x.name)
        return response.corpus

    def calculate_corpus_size(self, corpus_id: int):
        payload = {'customer_id': self.customer_id, 'corpus_id': corpus_id}
        resp = self.request_util.request("compute-corpus-size", payload, CalculateCorpusSizeResponse)
        return resp

    def get_usage_metrics_range(self, corpus_id: int, from_ts: int = None,to_ts: int = None,
                                bucket: int = None):
        """
        Adaption on top for GetUsageMetrics (/v1/get-usage-metrics) with provides a facade to
        retrieve an arbitrary range, group usage by the
        specified bucket.

        :param corpus_id: the corpus to query
        :param from_ts: the UNIX epoch start date for the range (inclusive). If None, it will be for 1 hour ago, on the
            minute.
        :param to_ts: the UNIX epoch end date for the range (exclusive). If None, it will be set for 1 hour after the
            from_ts
        :param bucket: how we will group usage, minimum and default here is 60s
        :return: a list of usage statistics, with the epoch and count with wrapping for the parameters used/inferred
        """

        now_ts = datetime.now()

        if from_ts:
            # Defensive Checks that this isn't after now.
            self.logger.debug("")

        else:
            # Set default
            temp_ts = datetime.now()
            from_ts = temp_ts.replace(tzinfo=timezone.utc)




    def read_corpus(self, corpus_id: int) -> CorpusInfo:
        request = ReadCorpusRequest([corpus_id], True, True, True, True, True, True)
        payload = asdict(request)
        response = self.request_util.request("read-corpus", payload, ReadCorpusResponse)
        # TODO Validate that there is 1 corpus and what happens if it doesn't exist.
        return response.corpora[0]

    def _create_corpus_inner(self, request: CreateCorpusRequest) -> CreateCorpusResponse:
        payload = asdict(request, dict_factory=_custom_asdict_factory)
        response = self.request_util.request("create-corpus", payload, CreateCorpusResponse)
        if response.status.code == StatusCode.OK:
            self.logger.info(f"Created new corpus with {response.corpusId}")
            return response
        else:
            raise Exception(f"Unable to create corpus due to: {response.status}")

    def create_corpus_d(self, corpus: Corpus) -> CreateCorpusResponse:
        request = CreateCorpusRequest(corpus)
        return self._create_corpus_inner(request)

    def create_corpus(self, name=None, description: str = None, custom_dimensions: List[Dimension] = None,
                      filter_attributes: List[FilterAttribute] = None) -> CreateCorpusResponse:

        # First create our domain request
        corpus = from_dict(Corpus, {
            'name': name,
            'description': description,
            'customDimensions': custom_dimensions,
            'filterAttributes': filter_attributes
        })
        request = CreateCorpusRequest(corpus)
        return self._create_corpus_inner(request)

    def delete_corpus(self, corpus_id: int) -> Status:
        request = DeleteCorpusRequest(self.customer_id, corpus_id)
        payload = asdict(request)

        response = self.request_util.request("delete-corpus", asdict(request), DeleteCorpusResponse)
        return response.status

    def create_api_key(self, corpus_id: Union[int, List], key_type: ApiKeyType, description: str = None):
        # Convert singular int to List of corpus ids.
        if type(corpus_id) is list:
            corpus_ids = corpus_id
        else:
            corpus_ids = [corpus_id]

        inner_payload = {"corpusId": corpus_ids, "apiKeyType": key_type.name}
        if description:
            inner_payload['description'] = description

        payload = {"apiKeyData": [inner_payload]}
        response = self.request_util.request("create-api-key", payload, CreateApiKeyResponse)
        status = response.response[0].status
        if status.code == StatusCode.OK:
            return response.response[0].keyId
        else:
            raise Exception(f"Unexpected response [{status}]")

    def _check_ok(self, response):
        status = response.status[0]
        if status.code != StatusCode.OK:
            raise Exception(f"Unexpected response [{status}]")

    def delete_api_key(self, key_id: Union[str, List[str]]):
        if type(key_id) is list:
            key_ids = key_id
        else:
            key_ids = [key_id]
        payload = {"keyId": key_ids}
        response = self.request_util.request("delete-api-key", payload, ModifyApiKeyResponse)
        self._check_ok(response)

    def update_api_key(self, key_id: str, enabled: bool):
        payload = {"keyEnablement": [{"keyId": key_id, "enable": enabled}]}
        response = self.request_util.request("enable-api-key", payload, ModifyApiKeyResponse)
        self._check_ok(response)

    def _list_api_keys(self, num_results: int = 10, page: str = None, read_corpora_info=True) -> ListApiKeysResponse:
        payload = {"numResults": num_results, "pageKey": page, "readCorporaInfo": read_corpora_info}
        #payload = {"numResults": num_results, "readCorporaInfo": read_corpora_info}
        response = self.request_util.request("list-api-keys", payload, ListApiKeysResponse)
        return response

    def list_api_keys(self,
                      # Filters
                      corpus_id:int=None, enabled:bool=None, key_type:ApiKeyType=None, key_status:ApiKeyStatus=None,
                      # Pagination
                      pagination:bool = False, page:int=1, page_size=10,
                      # Sort Params
                      sort_field:ApiKeySort=ApiKeySort.START_TS, sort_dir:SortDirection=SortDirection.ASC):
        """
        FIXME: MOVE Pagination/Sorting into vectara_client-client-manager.

        :param corpus_id:
        :param enabled:
        :param key_type:
        :param key_status:
        :param pagination:
        :param page:
        :param page_size:
        :param sort_field:
        :param sort_dir:
        :return:
        """

        # Retrieve all the API keys.

        self.logger.info(f"Getting first page")
        # FIXME Increase this to 1000 after testing to reduce pages.
        api_key_response = self._list_api_keys()
        self.logger.info(f"Found [{len(api_key_response.keyData)}] results")
        api_keys = api_key_response.keyData
        while api_key_response.pageKey:
            self.logger.info(f"Getting page [{api_key_response.pageKey}]")
            # FIXME Increase this to 1000 after testing to reduce pages.
            api_key_response = self._list_api_keys(page=api_key_response.pageKey)
            self.logger.info(f"Found [{len(api_key_response.keyData)}] results")
            api_keys.extend(api_key_response.keyData)

        # Filter
        if corpus_id or enabled or key_type or key_status:
            filtered_api_keys = []
            for api_key in api_keys:
                retain = True
                if corpus_id:
                    found = False
                    for corpus in api_key.corpus:
                        if corpus_id == corpus.id:
                            found = True
                            break
                    if not found:
                        retain = False

                if enabled is not None and enabled != api_key.apiKey.enabled:
                    retain = False
                elif key_type is not None and key_type != api_key.apiKey.keyType:
                    retain = False
                elif key_status is not None and key_status != api_key.apiKey.status:
                    retain = False

                if retain:
                    filtered_api_keys.append(api_key)
        else:
            filtered_api_keys = api_keys

        return filtered_api_keys


class CorpusBuilder:

    corpus: Corpus

    def __init__(self, name: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.corpus = from_dict(Corpus, {
            'name': name,
            'customDimensions': [],
            'filterAttributes': []
        })

    def name(self, name: str):
        self.corpus.name = name
        return self

    def description(self, description: str):
        self.corpus.description = description
        return self

    def add_attribute(self, name: str, description: str, indexed: bool = True, type: str = "text",
                      document: bool = True):
        """
        Adds a filter attribute to the given corpus.

        :param name: The name of this corpus.
        :param description: Description for this filter attribute.
        :param indexed: Whether this attribute is indexed (defaults to True)
        :param type: the type is taken from the FilterAttributeType and defaults to "text". This is matched to
        FilterAttributeType.FILTER_ATTRIBUTE_TYPE__TEXT
        :param document: Whether this is at the "document" or the "document_part"
        :return: ourselves
        """
        filter_attribute_type = None
        for filter_enum in FilterAttributeType:

            end_part = filter_enum.name.split("__")[1]
            if end_part == type.upper():
                filter_attribute_type = filter_enum
                break
        if not filter_attribute_type:

            raise Exception(f"Unknown FilterAttributeType [{type}]")

        level = None
        if document:
            level = FilterAttributeLevel.FILTER_ATTRIBUTE_LEVEL__DOCUMENT
        else:
            level = FilterAttributeLevel.FILTER_ATTRIBUTE_LEVEL__DOCUMENT_PART

        attribute_dict = {
            "name": name,
            "description": description,
            "indexed": indexed,
            "type": filter_attribute_type,
            "level": level
        }
        attribute = from_dict(FilterAttribute, attribute_dict)

        self.corpus.filterAttributes.append(attribute)
        return self

    def add_custom_dimension(self, name: str, description: str):
        # TODO Implement
        return self

    def build(self):
        return self.corpus




