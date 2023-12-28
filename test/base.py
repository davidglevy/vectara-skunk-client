from unittest import TestCase
import logging
from vectara.core import Factory
from vectara.domain import Corpus
from dacite import from_dict
import os

class BaseClientTest(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.basicConfig(format='%(asctime)s:%(name)-35s %(levelname)s:%(message)s', level=logging.INFO, datefmt='%H:%M:%S %z')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_corpus_name = self.__class__.__name__

    def setUp(self):
        self.logger.info("Loading Vectara Client")

        test_config = "." + os.sep + ".vectara_test_config"
        factory = Factory(config_path=test_config, profile="admin")
        self.client = factory.build()

        self.admin_service = self.client.admin_service
        self.indexer_service = self.client.indexer_service
        #self.query_service = self.client.query_service