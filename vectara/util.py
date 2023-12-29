from abc import ABC
from enum import Enum
from vectara.authn import BaseAuthUtil
from vectara.domain import UploadDocumentResponse, ResponseSet, Response, ResponseDocument, SummaryResponse
from typing import Type, TypeVar, List
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

    return dict((k, convert_value(v)) for k, v in data if v is not None)

    # lambda x: {k: v for (k, v) in x if v is not None}


class RequestUtil:

    def __init__(self, auth_util: BaseAuthUtil):
        self.logger = logging.getLogger(__class__.__name__)
        self.auth_util = auth_util

    def request(self, operation: str, payload, to_class: Type[T], method="POST") -> T:
        """

        :param operation: the REST operation to perform.
        :param payload: the payload which will be serialized.
        :return:
        """
        headers = self.auth_util.get_headers()
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        self.logger.debug(f"Headers: {json.dumps(headers)}")

        url = f"https://api.vectara.io/v1/{operation}"
        self.logger.info(f"URL for operation {operation} is: {url}")
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Payload is: {json.dumps(payload, indent=4)}")

        payload_json = json.dumps(payload)

        response = requests.request(method, url, headers=headers, data=payload_json)

        if response.status_code == 200:
            return from_dict(to_class, json.loads(response.text))
        else:
            self.logger.error(f"Received non 200 response {response.status_code}, throwing exception")
            response.raise_for_status()

    def multipart_post(self, operation: str, path_str: str = None, input_contents: bytes = None,
                       input_file_name: str = None,
                       params=None, headers=None) -> UploadDocumentResponse:

        # Create headers, taking in any from the particular method.
        if not headers:
            headers = {}

        sec_headers = self.auth_util.get_headers()
        for sec_header in sec_headers.keys():
            headers[sec_header] = sec_headers[sec_header]

        self.logger.debug(f"Headers: {json.dumps(headers)}")

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
                Need to ignore tqdm std.py:580: DeprecationWarning: datetime.datetime.utcfromtimestamp()
                
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
                            return from_dict(UploadDocumentResponse, json.loads(response.text))
                        else:
                            self.logger.error(f"Received non 200 response {response.status_code}: {response.text}")
                            response.raise_for_status()

        elif input_file_name:
            raise Exception("Re-implement after refactor")
            # files={'file': (input_file_name, input_contents), 'c': self.customer_id, 'o': corpus_id}


class BaseFormatter(ABC):

    def __init__(self):
        pass

    def heading(self, heading: str, level: int = 1):
        raise Exception("Implement in subclass")

    def sentence(self, sentence: str):
        raise Exception("Implement in subclass")

    def link(self, text: str, url: str):
        raise Exception("Implement in subclass")

    def paragraph(self, paragraph: str):
        raise Exception("Implement in subclass")

    def bold(self, text: str):
        raise Exception("Implement in subclass")

    def italic(self, text: str):
        raise Exception("Implement in subclass")

    def list(self, items: List[str], level: int = 1):
        raise Exception("Implement in subclass")

    def rtl(self, text: str):
        raise Exception("Implement in subclass")


class MarkdownFormatter(BaseFormatter):

    def __init__(self):
        pass

    def heading(self, heading: str, level: int = 1):
        indent = "#" * level
        return f'\n{indent} {heading}'

    def sentence(self, sentence: str):
        return sentence

    def link(self, text, url):
        return f"[{text}]({url})"

    def paragraph(self, paragraph: str):
        return f"\n\n{paragraph}\n"

    def bold(self, text: str):
        return f"**{text}**"

    def italic(self, text: str):
        return f"*{text}*"

    def list(self, items: List[str], level: int = 1):
        if level < 1:
            raise TypeError("List level must be greater than 0")
        indent = " " * (level - 1)
        results = [f"{indent} {idx + 1}. {item}" for idx, item in enumerate(items)]
        return "\n" + "\n".join(results) + "\n"

    def rtl(self, text):
        return '<div dir="rtl">\n' + text + '</div>'

class ResponseSetRenderer:

    def __init__(self, formatter: BaseFormatter):
        self.formatter = formatter

    def render(self, query: str, responseSet: ResponseSet, rtl=False):
        f = self.formatter
        results = []

        # Build Heading
        results.append(f.heading(f"Query: {query}"))

        # Build Summary
        if len(responseSet.summary) > 0:
            summary_text = responseSet.summary[0].text
            results.append(f.paragraph(summary_text))

        # Build items
        docs = []
        for result in responseSet.response:
            doc_index = result.documentIndex
            doc = responseSet.document[doc_index]

            item = f.sentence(result.text) + " " + f.italic("score: " + str(result.score) + ", doc-id: " + doc.id)
            docs.append(item)

        list_text = f.list(docs)
        results.append(list_text)

        # TODO Build document list.

        results = "".join(results)
        if rtl:
            return f.rtl(results)


def render_markdown(query: str, response_set: ResponseSet):
    formatter = MarkdownFormatter()
    renderer = ResponseSetRenderer(formatter)
    return renderer.render(query, response_set)
