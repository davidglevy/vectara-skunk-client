from typing import List

import requests

from vectara.authn import BaseAuthUtil
from vectara.domain import UploadDocumentResponse, CoreDocument, IndexDocumentRequest, IndexDocumentResponse
from vectara.util import RequestUtil
from typing import Union
from pathlib import Path
from dacite import from_dict
from dataclasses import asdict
import logging
import json
import os


class IndexerService():

    def __init__(self, auth_util:BaseAuthUtil, request_util: RequestUtil, customer_id: int):
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

        params['doc_metadata'] = json.dumps(metadata)

        return self.request_util.multipart_post("upload", path_str=path, input_contents=input_contents, input_file_name=input_file_name, params=params, headers=headers)

    # def upload_old(self, corpus_id: int, path: str = None, input_contents: bytes = None, input_file_name: str = None,
    #                return_extracted: bool = None, metadata: dict = None) -> UploadDocumentResponse:
    #
    #     files = None
    #     if path and input_file_name:
    #         raise TypeError("You must specify either the path or the file_name")
    #     elif path:
    #         file_name = path.split(os.sep)[-1]
    #
    #         with open(path, 'rb') as f:
    #             contents = f.read()
    #
    #         files = {'file': (file_name, contents), 'c': self.customer_id, 'o': corpus_id}
    #     elif input_file_name:
    #         files = {'file': (input_file_name, input_contents), 'c': self.customer_id, 'o': corpus_id}
    #
    #     if metadata:
    #         files['doc_metadata'] = json.dumps(metadata)
    #
    #     headers = self.auth_util.get_headers()
    #     #headers['c'] = str(self.customer_id)
    #     #headers['o'] = str(corpus_id)
    #
    #     self.logger.info(f"Headers: {json.dumps(headers)}")
    #
    #     params = {'c': self.customer_id, 'o': corpus_id}
    #     if return_extracted:
    #         params['d'] = True
    #
    #     url = f"https://api.vectara.io/v1/upload"
    #     response = requests.post(url, headers=headers, files=files, params=params)
    #
    #     print(response)
    #
    #     if response.status_code == 200:
    #         index_response = from_dict(UploadDocumentResponse, json.loads(response.text))
    #         return index_response
    #     else:
    #         self.logger.error(f"Received non 200 response {response.status_code}, throwing exception")
    #         response.raise_for_status()



    def delete(self, corpus_id: int, document_id: str):
        delete_request = {'customer_id': self.customer_id, 'corpus_id': corpus_id, 'document_id': document_id}

        response = self.request_util.request('delete-doc', delete_request)
        return response