"""
This module contains the IndexerService class.

@Author: David Levy
@Date: 4/1/2024 (dd/mm/yyyy)
@Links: https://docs.vectara.com/docs/api-reference/indexing-apis/indexing
@Links: https://docs.vectara.com/docs/api-reference/indexing-apis/file-upload/file-upload
@Links: https://docs.vectara.com/docs/api-reference/indexing-apis/deleting-documents

Tasks
* TODO We should provide a method to check prior uploads via sha1_hash as per BaseClientTest
* TODO There's likely a higher abstraction here which will check for doc existing and allow overwrites (CorpusManager?)
* TODO Investigate whether I need the lower level API too
"""
from vectara.authn import BaseAuthUtil
from vectara.domain import UploadDocumentResponse, CoreDocument, IndexDocumentRequest, IndexDocumentResponse
from vectara.util import RequestUtil
from typing import Union
from pathlib import Path
from dacite import from_dict
from dataclasses import asdict
import logging
import json


class IndexerService:
    """
    Wrapper for the Vectara index REST API

    One instantiation per customer id

    """

    def __init__(self, auth_util: BaseAuthUtil, request_util: RequestUtil, customer_id: int):
        """
        Inject the dependencies for IndexerService that are configured in our factory

        :param auth_util: dependent authentication utility
        :param request_util: dependent request utility
        :param customer_id: the customer id for this account
        """
        self.logger = logging.getLogger(__class__.__name__)
        self.request_util = request_util
        self.customer_id = customer_id
        self.auth_util = auth_util

    def index_doc(self, corpus_id: int, document: Union[dict, CoreDocument]):
        """
        Indexes the give document which is already in a format that is ready to be added to the embedding.

        It is worth noting that this API can either take a dict or a CoreDocument, however the dict will
        be validated against the CoreDocument schema.

        :param corpus_id: the corpus to put the document in
        :param document: either a dict which will be validated against CoreDocument, or a CoreDocument.
        :return:
        """
        # Convert singular int to List of corpus ids.
        if type(document) is dict:
            domain = from_dict(CoreDocument, document)
        else:
            domain = document

        # Now Convert back to dict, knowing that our parameter is type safe.
        # FIXME Ask Tallat why the customer ID for this API is an integer (unexpected)
        request = IndexDocumentRequest(int(self.customer_id), corpus_id, domain)
        payload = asdict(request)

        result = self.request_util.request('index', payload, to_class=IndexDocumentResponse)
        return result


    def upload(self, corpus_id: int, path: Union[str, Path] = None, input_contents: bytes = None, input_file_name: str = None,
               return_extracted: bool = None, metadata: dict = None) -> UploadDocumentResponse:
        headers = {'c': str(self.customer_id), 'o': str(corpus_id)}
        self.logger.info(f"Headers: {json.dumps(headers)}")

        params = {'c': str(self.customer_id), 'o': str(corpus_id)}
        if return_extracted:
            params['d'] = str(True)

        if metadata:
            params['doc_metadata'] = json.dumps(metadata)

        return self.request_util.multipart_post("upload", path_str=path, input_contents=input_contents, input_file_name=input_file_name, params=params, headers=headers)


    def delete(self, corpus_id: int, document_id: str):
        delete_request = {'customer_id': self.customer_id, 'corpus_id': corpus_id, 'document_id': document_id}

        response = self.request_util.request('delete-doc', delete_request)
        return response