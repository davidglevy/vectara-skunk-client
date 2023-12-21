from typing import List

import requests

from vectara.authn import BaseAuthUtil
from vectara.domain import UploadDocumentResponse
import logging
import json
import os
from dacite import from_dict

class IndexerService():

    def __init__(self, auth_util: BaseAuthUtil, customer_id: int):
        self.logger = logging.getLogger(__class__.__name__)
        self.auth_util = auth_util
        self.customer_id = customer_id


    def upload(self, corpus_id:int, path:str=None, input_contents:bytes=None, input_file_name:str=None, return_extracted:bool=None, metadata:dict=None) -> UploadDocumentResponse:

        files = None
        if path and input_file_name:
            raise TypeError("You must specify either the path or the file_name")
        elif path:
            file_name = path.split(os.sep)[-1]

            with open(path, 'rb') as f:
                contents = f.read()

            files={'file': (file_name, contents), 'c': self.customer_id, 'o': corpus_id }
        elif input_file_name:
            files={'file': (input_file_name, input_contents), 'c': self.customer_id, 'o': corpus_id}

        if metadata:
            files['doc_metadata'] = json.dumps(metadata)

        headers = self.auth_util.get_headers()
        headers['c'] = str(self.customer_id)
        headers['o'] = str(corpus_id)

        self.logger.info(f"Headers: {json.dumps(headers)}")

        params= {'c': self.customer_id, 'o': corpus_id}
        if return_extracted:
            params['d'] = True

        url = f"https://api.vectara.io/v1/upload"
        response = requests.post(url, headers=headers, files=files, params=params)

        print(response)

        if response.status_code == 200:
           indexResponse = from_dict(UploadDocumentResponse, json.loads(response.text))
           return indexResponse
        else:
           self.logger.error(f"Received non 200 response {response.status_code}, throwing exception")
           response.raise_for_status()

