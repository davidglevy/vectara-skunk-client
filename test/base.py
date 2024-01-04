from unittest import TestCase
import logging
from vectara.core import Factory, Client
from vectara.domain import (Corpus, FilterAttribute, FilterAttributeType, FilterAttributeLevel, UploadDocumentResponse,
                            IndexDocumentResponse)
from vectara.query import QueryService
from vectara.admin import AdminService
from vectara.index import IndexerService

from typing import Union
from dacite import from_dict
from pathlib import Path

import os
import hashlib
import getpass
import json

# 64KBs chunks
SHA1_BUFF_SIZE = 65536

def calculate_sha1(file_path):
    """
    Efficiently calculate the SHA1 hash for a file.

    :param file_path:
    :return:
    """
    sha1 = hashlib.sha1()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(SHA1_BUFF_SIZE)
            if not data:
                return sha1.hexdigest()
            sha1.update(data)



class BaseClientTest(TestCase):

    client: Client
    query_service: QueryService
    admin_service: AdminService
    indexer_service: IndexerService
    corpus_id: int
    test_corpus_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.basicConfig(format='%(asctime)s:%(name)-35s %(levelname)s:%(message)s', level=logging.INFO, datefmt='%H:%M:%S %z')

        self.logger = logging.getLogger(self.__class__.__name__)

        # use the class and test name for the name
        test_parts = [getpass.getuser()]
        test_parts.extend(self.id().split(".")[-2:])
        self.test_corpus_name = ".".join(test_parts)[0:50]


    def _create_corpus_filter_attrs(self):
        sha1_hash_attr = FilterAttribute("sha1_hash", "SHA1 hash of the content", False,
                                         FilterAttributeType.FILTER_ATTRIBUTE_TYPE__TEXT,
                                         FilterAttributeLevel.FILTER_ATTRIBUTE_LEVEL__DOCUMENT)
        return [sha1_hash_attr]

    def setUp(self):
        super().setUp()
        self.logger.info("Loading Vectara Client")


        test_config = "." + os.sep + ".vectara_test_config"
        factory = Factory(config_path=test_config, profile="admin")
        self.client = factory.build()

        self.admin_service = self.client.admin_service
        self.indexer_service = self.client.indexer_service
        self.query_service = self.client.query_service

        # TODO If environ flag "rebuild" is set to true, delete existing test corpora and re-create.
        # Check if test corpus exists
        corpora = self.admin_service.list_corpora(self.test_corpus_name)

        #    # TODO temporarily ignore this option.
        if len(corpora) == 1:
            self.logger.info("Found existing test corpus")
            self.corpus_id = corpora[0].id
        #    self.logger.info("TODO - DELETE, temporarily deleting corpora through each run.")
        #    self.admin_service.delete_corpus(corpora[0].id)
        elif len(corpora) > 1:
            # TODO Rework logic so we can support tests with multiple corpus
            raise Exception("Unexpected configuration - multiple matching corpora for test name.")
        else:
            # Create new corpora
            description = self.shortDescription()
            if not description:
                description = "Corpus to support test. TODO - set docstring in test for more informative text."

            resp = self.admin_service.create_corpus(name=self.test_corpus_name,
                                             description=description,
                                             filter_attributes=self._create_corpus_filter_attrs())
            self.corpus_id = resp.corpusId

    def upload_test_doc(self, doc_name:str, force=False, metadata:dict=None) -> Union[UploadDocumentResponse, None]:
        """
        Uploads a binary document via the upload API.
        :param doc_name: the path to our file to upload
        :param force: upload our test document even if already present, this may be useful when checking response
        :param metadata: additional metadata to add to the documednt
        :return:
        """
        path = Path(doc_name)
        self.logger.info(f"Checking if we need to upload test Document [{path.name}]")

        # Get the SHA1 hash of the test doc.
        sha1_hash = calculate_sha1(doc_name)

        # Run a query without summarization with a doc_id and metadata sha1 hash check
        metadata_filter = f"doc.id = '{path.name}'"
        resp = self.query_service.query(path.name, self.corpus_id, summary=False, metadata=metadata_filter)

        upload = False
        if force:
            self.logger.info("Forcing upload")
            upload = True

        if len(resp.document) == 0:
            self.logger.info("No existing documents, will upload test document.")
            upload = True
        elif len(resp.document) > 1:
            raise Exception(f"Two documents found with same id [{path.name}]")
        else:
            # If found, do nothing.
            existing_sha1_hash = ""
            for metadata_attr in resp.document[0].metadata:
                if metadata_attr.name == 'sha1_hash':
                    existing_sha1_hash = metadata_attr.value
                    break
            if existing_sha1_hash != sha1_hash or force:
                # We had to introduce 'or force', as a change in metadata doesn't change the core sha1 has of document
                self.logger.info(f"Test document [{path.name}] hash different SHA1 hash to repository, re-uploading")
                self.indexer_service.delete(self.corpus_id, path.name)
                upload = True
            else:
                self.logger.info("Existing test document has correct sha1_hash, no need to recreate")

        # If not found, upload.
        if upload:
            self.logger.info(f"Uploading test document [{path}]")
            if metadata:
                metadata['sha1_hash'] = sha1_hash
            else:
                metadata = {'sha1_hash': sha1_hash}
            return self.indexer_service.upload(self.corpus_id, path, metadata=metadata)
        else:
            return None

    def index_test_doc(self, doc_name, force=False) -> Union[IndexDocumentResponse, None]:
        path = Path(doc_name)
        self.logger.info(f"Checking if we need to index test Document [{path.name}]")

        # Get the SHA1 hash of the test doc.
        sha1_hash = calculate_sha1(path)

        with open(path, 'r') as f:
            document_dict = json.loads(f.read())

        doc_id = document_dict['document_id']
        # Run a query without summarization with a doc_id and metadata sha1 hash check
        metadata_filter = f"doc.id = '{doc_id}'"
        resp = self.query_service.query(path.name, self.corpus_id, summary=False, metadata=metadata_filter)

        index = False
        if force:
            self.logger.info("Force index set, we will send document to be indexed, overriding existing")
            index = True

        if len(resp.document) == 0:
            self.logger.info("No existing documents, will index test document.")
            index = True
        elif len(resp.document) > 1:
            raise Exception(f"Two documents found with same id [{doc_id}]")
        else:
            # Check sha1hash
            existing_sha1_hash = ""
            for metadata in resp.document[0].metadata:
                if metadata.name == 'sha1_hash':
                    existing_sha1_hash = metadata.value
                    break
            if existing_sha1_hash != sha1_hash:
                self.logger.info(f"Test document [{doc_id}] hash different SHA1 hash to repository, re-uploading")
                self.indexer_service.delete(self.corpus_id, doc_id)
                index = True
            else:
                self.logger.info("Existing test document has correct sha1_hash, no need to recreate")

        # If not found, upload.
        if index:
            self.logger.info(f"Indexing test document [{path}]")
            # Add in Sha1Hash to found metadata.
            if 'metadata_json' in document_dict:
                repl_metadata = json.loads(document_dict['metadata_json'])
                repl_metadata['sha1_hash'] = sha1_hash
            else:
                repl_metadata = {'sha1_hash': sha1_hash}
            document_dict['metadata_json'] = json.dumps(repl_metadata)

            return self.indexer_service.index_doc(self.corpus_id, document_dict)
        else:
            return None


