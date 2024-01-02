import json
from unittest import TestCase
from vectara.util import render_markdown, SimplePromptFactory
from vectara.domain import ResponseSet
from dacite import from_dict


class RenderMarkdownTest(TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

    def buildResponseSet(self):
        responseSet = {
            'response': [
                {
                    'text': 'In document abc we found x',
                    'score': 0.8845,
                    'metadata': [
                        {
                            "name": "lang",
                            "value": "eng"
                        },
                        {
                            "name": "section",
                            "value": "1"
                        },
                        {
                            "name": "offset",
                            "value": "0"
                        },
                        {
                            "name": "len",
                            "value": "94"
                        }
                    ],
                    "corpusKey": {
                        "corpusId": 112,
                        "customerId": 0,
                        "semantics": "DEFAULT",
                        "dim": [],
                        "metadataFilter": "",
                        "lexicalInterpolationConfig": None
                    },
                    "resultOffset": 0
                },
                {
                    'text': 'In document def we found y',
                    'score': 0.778,
                    'metadata': [
                        {
                            "name": "lang",
                            "value": "eng"
                        },
                        {
                            "name": "section",
                            "value": "1"
                        },
                        {
                            "name": "offset",
                            "value": "0"
                        },
                        {
                            "name": "len",
                            "value": "94"
                        }
                    ],
                    "corpusKey": {
                        "corpusId": 112,
                        "customerId": 0,
                        "semantics": "DEFAULT",
                        "dim": [],
                        "metadataFilter": "",
                        "lexicalInterpolationConfig": None
                    },
                    "resultOffset": 0
                },
                {
                    'text': 'In document ghi we found z',
                    'score': 0.5151,
                    'metadata': [
                        {
                            "name": "lang",
                            "value": "eng"
                        },
                        {
                            "name": "section",
                            "value": "1"
                        },
                        {
                            "name": "offset",
                            "value": "0"
                        },
                        {
                            "name": "len",
                            "value": "94"
                        }
                    ],
                    "corpusKey": {
                        "corpusId": 112,
                        "customerId": 0,
                        "semantics": "DEFAULT",
                        "dim": [],
                        "metadataFilter": "",
                        "lexicalInterpolationConfig": None
                    },
                    "resultOffset": 0
                }
            ],
            'status': [],
            'summary': [
                {
                    'text': 'We found some awesome results',
                    'lang': 'en',
                    'prompt': '1.2.0 awesome summarizer',
                    'status': []
                }
            ]

        }
        return from_dict(ResponseSet, responseSet)

    def testRenderMarkdown(self):
        responseSet = self.buildResponseSet()
        result = render_markdown("Some awesome question", responseSet)

        print(result)

    def testSimplePromptFactory(self):
        factory = SimplePromptFactory(system_text='You are a human resources manager who takes the search results and summarizes them as a coherent response. Only use information provided in this chat. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\"."', user_text="")

        prompt = factory.build()


        print(prompt)

