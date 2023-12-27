import unittest
import logging
from vectara.core import Factory
import json
import os

logging.basicConfig(
        format=logging.BASIC_FORMAT, level=logging.INFO)


class QueryServiceIntegrationTest(unittest.TestCase):


    def setUp(self):
        print(os.getcwd())

        test_config = "." + os.sep + ".vectara_test_config"
        factory = Factory(config_path=test_config, profile="admin")
        client = factory.build()

        self.queryService = client.query_service

    def testQueryCorpora(self):
        """
        Run a test over corpora

        TODO Make the corpora id dynamic and refreshed by a "start" test.
        :return:
        """
        corpora = self.queryService.query("Which state has the fastest internet speeds in Australia?", 6)
