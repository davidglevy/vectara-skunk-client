from enum import Enum
from vectara.authn import BaseAuthUtil
from vectara.domain import UploadDocumentResponse
from typing import Type, TypeVar
from dacite import from_dict
from pathlib import Path
from tqdm import tqdm
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import logging
import json
import requests
import warnings
import os

T = TypeVar("T")


def _custom_asdict_factory(data):
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.name
        return obj

    return dict((k, convert_value(v)) for k, v in data)


class RequestUtil:

    def __init__(self, auth_util: BaseAuthUtil):
        self.logger = logging.getLogger(__class__.__name__)
        self.auth_util = auth_util

    def _upload_file(upload_url, fields, filepath):

        path = Path(filepath)
        total_size = path.stat().st_size
        filename = path.name

        with tqdm(
                desc=filename,
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            with open(filepath, "rb") as f:
                fields["file"] = ("filename", f)
                e = MultipartEncoder(fields=fields)
                m = MultipartEncoderMonitor(
                    e, lambda monitor: bar.update(monitor.bytes_read - bar.n)
                )
                headers = {"Content-Type": m.content_type}
                requests.post(upload_url, data=m, headers=headers)

    def request(self, operation: str, payload, to_class: Type[T], method="POST") -> T:
        """

        :param operation: the REST operation to perform.
        :param payload: the payload which will be serialized.
        :return:
        """
        headers = self.auth_util.get_headers()
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        self.logger.info(f"Headers: {json.dumps(headers)}")

        url = f"https://api.vectara.io/v1/{operation}"
        self.logger.info(f"URL for operation {operation} is: {url}")
        self.logger.info(f"Payload is: {json.dumps(payload, indent=4)}")

        payload_json = json.dumps(payload)

        response = requests.request(method, url, headers=headers, data=payload_json)

        if response.status_code == 200:
            return from_dict(to_class, json.loads(response.text))
        else:
            self.logger.error(f"Received non 200 response {response.status_code}, throwing exception")
            response.raise_for_status()

    def multipart_post(self, operation: str, path_str:str=None, input_contents:bytes=None, input_file_name:str=None,
                       params=None, headers=None) -> UploadDocumentResponse:

        # Create headers, taking in any from the particular method.
        if not headers:
            headers = {}

        sec_headers = self.auth_util.get_headers()
        for sec_header in sec_headers.keys():
            headers[sec_header] = sec_headers[sec_header]

        self.logger.info(f"Headers: {json.dumps(headers)}")


        upload_url = f"https://api.vectara.io/v1/{operation}"

        files = None
        if path_str and input_file_name:
            raise TypeError("You must specify either the path or the file_name")
        elif path_str:
            path = Path(path_str)
            tracker_total_size = path.stat().st_size
            tracker_file_name = path.name

            with warnings.catch_warnings(action="ignore"):
                """
                Need to ignore tqdm\std.py:580: DeprecationWarning: datetime.datetime.utcfromtimestamp()
                
                See more here: https://github.com/tqdm/tqdm/issues/1517                
                """
                with tqdm(
                    desc=tracker_file_name,
                    total=tracker_total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024
                ) as bar:

                    with open(path, 'rb') as f:

                        # TODO Get mimetype for extension.

                        if params:
                            params['file'] = (tracker_file_name, f, 'application/pdf')
                        else:
                            params = {'file': (tracker_file_name, f, 'application/pdf')}

                        # This doesn't yet include the boundary

                        encoder = MultipartEncoder(fields=params)

                        headers['Content-Type'] = encoder.content_type

                        m = MultipartEncoderMonitor(
                            encoder, lambda monitor: bar.update(monitor.bytes_read - bar.n)
                        )

                        response = requests.post(upload_url, data=m, headers=headers)

                        if response.status_code == 200:
                            return response
                        else:
                            self.logger.error(f"Received non 200 response {response.status_code}: {response.text}")
                            response.raise_for_status()

        elif input_file_name:
            raise Exception("Re-implement after refactor")
            #files={'file': (input_file_name, input_contents), 'c': self.customer_id, 'o': corpus_id}

