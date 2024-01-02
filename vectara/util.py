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

    def render(self, query: str, responseSet: ResponseSet, rtl=False, show_search_results=True):
        f = self.formatter
        results = []

        # Build Heading
        results.append(f.heading(f"Query: {query}"))

        # Build Summary
        if len(responseSet.summary) > 0:
            summary_text = responseSet.summary[0].text
            results.append(f.paragraph(summary_text))

        # Build items
        if show_search_results:
            docs = []
            for result in responseSet.response:
                doc_index = result.documentIndex
                doc = responseSet.document[doc_index]

                item = f.sentence(result.text) + " " + f.italic("score: " + str(result.score) + ", doc-id: " + doc.id)
                docs.append(item)

            list_text = f.list(docs)
            results.append(list_text)

        # TODO Build document list.

        results_text = "".join(results)

        if rtl:
            return f.rtl(results_text)
        else:
            return results_text


def render_markdown(query: str, response_set: ResponseSet, rtl=False, show_search_results=True):
    formatter = MarkdownFormatter()
    renderer = ResponseSetRenderer(formatter)
    return renderer.render(query, response_set, rtl, show_search_results)


prompt_text = (
    '[ {"role": "system", "content": "You are a human resources manager who takes the search results and summarizes them as a coherent response. Only use information provided in this chat. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\"."}, \n'  # ,\n'
    '#foreach ($qResult in $vectaraQueryResults) \n'
    '   #if ($foreach.first) \n'
    '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n'
    '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
    '   #else \n'
    '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n'
    '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
    '   #end \n'
    ' #end \n'
    '{"role": "user", "content": "Generate a detailed answer (that is no more than 300 words) for the query \\"$esc.java(${vectaraQuery})\\" solely based on the search results in this chat. You must only use information from the provided results. Cite search results using \\"[number]\\" notation. Only cite the most relevant results that answer the question accurately." } ]')


class BasePromptFactory(ABC):

    def __init__(self):
        pass

    def build(self):
        raise Exception("Implement in subclasses")


class SimplePromptFactory(BasePromptFactory):
    SYSTEM_PROMPT_TEMPLATE = 'You are a {persona} who takes the search results and {a_cite_text} {just_rag_text} Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\".'
    USER_PROMPT_TEMPLATE = 'Generate a detailed answer (that is no more than {max_word_count} words) for the query \\"$esc.java(${{vectaraQuery}})\\" {just_rag_text} {b_cite_text}'

    A_DO_CITE = "summarizes them as a coherent response,"
    A_DO_NOT_CITE = "only return the most relevant answer. Do not iterate over each question,"

    B_DO_CITE = 'Cite search results using \\\\\\"[number]\\\\\\" notation. Only cite the most relevant results that answer the question accurately.'
    B_DO_NOT_CITE = 'Do not cite search results.'

    RAG_ONLY = 'solely based on the search results in this chat. You must only use information from the provided results.'
    ALLOW_NON_RAG = 'preferably based on the search results in this chat. You may allow additional information you know in the results.'

    """
    Generates a valid prompt text

    """

    def __init__(self, persona: str, max_word_count: int = 300, cite: bool = True, just_rag=True):
        super().__init__()
        self.persona = persona
        self.max_word_count = max_word_count
        self.cite = cite
        self.just_rag = just_rag

    def build(self):
        lines = []

        if self.just_rag:
            just_rag_text = SimplePromptFactory.RAG_ONLY
        else:
            just_rag_text = SimplePromptFactory.ALLOW_NON_RAG

        if self.cite:
            a_cite_text = SimplePromptFactory.A_DO_CITE
            b_cite_text = SimplePromptFactory.B_DO_CITE
        else:
            a_cite_text = SimplePromptFactory.A_DO_NOT_CITE
            b_cite_text = SimplePromptFactory.B_DO_NOT_CITE

        system_prompt = SimplePromptFactory.SYSTEM_PROMPT_TEMPLATE.format(
            persona=self.persona, just_rag_text=just_rag_text, a_cite_text=a_cite_text
        )

        user_prompt = SimplePromptFactory.USER_PROMPT_TEMPLATE.format(
            max_word_count=self.max_word_count, just_rag_text=just_rag_text, b_cite_text=b_cite_text
        )

        # Append the system indicator.
        lines.append(f'[ {{"role": "system", "content": "{system_prompt}"}}, \n')

        # Append the pre-requisite 'for-loop' for RAG.
        lines.append('#foreach ($qResult in $vectaraQueryResults) \n')
        lines.append('   #if ($foreach.first) \n')
        lines.append(
            '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #else \n')
        lines.append(
            '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #end \n')
        lines.append(' #end \n')

        # Append the Final user phrasing.
        # TODO interpolate.
        lines.append(f'{{"role": "user", "content": "{user_prompt}" }} ]')

        return "".join(lines)


class StandardPromptFactory(BasePromptFactory):
    """
    Generates a valid prompt text

    """

    def __init__(self, system_prompt=None, user_prompt=None):
        super().__init__()
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def build(self):
        lines = []
        # Append the system indicator.
        lines.append(f'[ {{"role": "system", "content": "{self.system_prompt}"}}, \n')

        # Append the pre-requisite 'for-loop' for RAG.
        lines.append('#foreach ($qResult in $vectaraQueryResults) \n')
        lines.append('   #if ($foreach.first) \n')
        lines.append(
            '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #else \n')
        lines.append(
            '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #end \n')
        lines.append(' #end \n')

        # Append the Final user phrasing.
        # TODO interpolate.
        lines.append(f'{{"role": "user", "content": "{self.user_prompt}" }} ]')

        return "".join(lines)


class ChatPromptFactory(BasePromptFactory):
    SYSTEM_PROMPT_TEMPLATE = 'You are a {chat_persona} talking with a customer, respond to small talk in a nice way. You must not say you are an AI model. Provide a short answer from the search results, though you can go into more detail if requested from the user. Do not iterate over each question, just provide a short answer based on prior assistant answers in this chat. You may allow additional information you know in the results if nothing relevant is found. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\".'
    USER_PROMPT_TEMPLATE = 'Generate a chat response which is part of a back-and-forth, that is no more than {max_word_count} words, for the query \\"$esc.java(${{vectaraQuery}})\\" preferably based on the interactions in this chat. Please ask for more information to help clarify if needed. If the response answers the question, please finish with a closing phrase that uses \\"does that answer your question\\" to confirm resolution.'

    def __init__(self, chat_persona="Customer Support", name="Gary", max_word_count=300):
        super().__init__()
        self.chat_persona = chat_persona
        self.name = name
        self.messages = []
        self.max_word_count = max_word_count

    def add_user_message(self, user_message):
        self.messages.append({"role": "user", "content": user_message})

    def add_assistant_message(self, assistant_message):
        self.messages.append({"role": "assistant", "content": assistant_message})

    def add_user_assistant_pair(self, user_message, assistant_message):
        self.messages.append({"role": "user", "content": user_message})
        self.messages.append({"role": "assistant", "content": assistant_message})

    def build(self):
        system_prompt = ChatPromptFactory.SYSTEM_PROMPT_TEMPLATE.format(
            chat_persona=self.chat_persona
        )

        user_prompt = ChatPromptFactory.USER_PROMPT_TEMPLATE.format(
            max_word_count=self.max_word_count
        )

        lines = []

        # Append the system indicator.
        lines.append(f'[ {{"role": "system", "content": "{system_prompt}"}}, \n')

        # Append the pre-requisite 'for-loop' for RAG.
        lines.append('#foreach ($qResult in $vectaraQueryResults) \n')

        # Insert prior context user/assistant messages.
        for message in self.messages:
            lines.append(f'    {json.dumps(message)}, \n')

        # Insert the Retrieval results.
        lines.append('   #if ($foreach.first) \n')
        lines.append(
            '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #else \n')
        lines.append(
            '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #end \n')
        lines.append(' #end \n')

        # Append the Final user phrasing.
        lines.append(f'{{"role": "user", "content": "{user_prompt}" }} ]')

        return "".join(lines)



