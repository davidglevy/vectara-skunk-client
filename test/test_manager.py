import unittest
import logging
from vectara.client.core import Factory
from vectara.client.manager import VectaraManager
from vectara.client.dao import ManagerDao, CorpusDao

import os

logging.basicConfig(
format='%(levelname)-5s:%(name)-35s:%(message)s', level=logging.INFO
)


class VectaraManagerIntTest(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.logger = logging.getLogger(__class__.__name__)
        self.test_corpus_name = __class__.__name__

    def setUp(self):
        self.logger.info("Loading Vectara Client")

        test_config = "." + os.sep + ".vectara_test_config"
        factory = Factory(config_path=test_config, profile="admin")
        client = factory.build()

        self.admin_service = client.admin_service
        self.indexer_service = client.indexer_service

        # Check existing corpus doesn't exist

        self.managerDao = ManagerDao()
        self.corpusDao = CorpusDao()

        self.target = VectaraManager(client, self.managerDao, self.corpusDao, self.admin_service)

    def test(self):
        # TODO Extract the manager from this project!!
        pass
        #self.target.sync_local_db()


