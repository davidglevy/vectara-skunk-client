from dataclasses import asdict
from vectara.client.domain import *
from vectara.client.enums import ApiKeyStatus, ApiKeyType, ApiKeySort, SortDirection
from dacite import from_dict
from typing import List, TypeVar, Union
from vectara.client.status import StatusCode
from vectara.client.util import _custom_asdict_factory, RequestUtil
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
        FIXME: MOVE Pagination/Sorting into vectara-client-manager.

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


