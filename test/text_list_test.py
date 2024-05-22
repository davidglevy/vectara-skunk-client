from vectara_client.core import Factory
from vectara_client.admin import CorpusBuilder
from dataclasses import asdict
import unittest
import json
import logging


class TextListTest(unittest.TestCase):

    def test_text_list(self):
        logging.basicConfig(format='%(asctime)s:%(name)-35s %(levelname)s:%(message)s', level=logging.DEBUG,
                            datefmt='%H:%M:%S %z')

        logger = logging.getLogger(self.__class__.__name__)

        client = Factory().build()
        corpus = (CorpusBuilder("text-list-attr")
                  .add_attribute("colors", "A list of colors", type="text_list")
                  .add_attribute("color", "A single color", type="text")
                  .build())

        corpus_id = client.corpus_manager.create_corpus(corpus, delete_existing=True)

        request = client.request_util.requests[-1]
        logger.info(f"Corpus creation request:\n{json.dumps(request, indent=4)}")

        metadata = {"colors": ["blue", "red"], "color": "green"}
        metadata_json = json.dumps(metadata)

        document = {
            "document_id": "doc-id-1",
            "title": "Rental 10 McMann St, Evatt",
            "metadata_json": metadata_json,
            "section": [
                {
                    "text": "A stunning four bedroom house overlooking a lake"
                }
            ]
        }

        client.indexer_service.index_doc(corpus_id, document)
        request = client.request_util.requests[-1]
        logger.info(f"Index request:\n{json.dumps(request, indent=4)}")

        document_after = client.document_service.list_documents(corpus_id)[0]

        logger.info(f"Document from corpus was:\n{json.dumps(asdict(document_after), indent=4)}")


