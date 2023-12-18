import unittest
import logging
from vectara.core import Factory
from test.util import loadTestConfigAsJson
import json
import os

logging.basicConfig(
        format=logging.BASIC_FORMAT, level=logging.INFO)


class AdminServiceIntegrationTest(unittest.TestCase):


    def setUp(self):
        print(os.getcwd())

        test_config_json = loadTestConfigAsJson("admin")

        factory = Factory(config_json=test_config_json)
        client = factory.build()

        self.adminService = client.admin_service

    def testListCorpora(self):

        corpora = self.adminService.list_corpora()



        for corpus in corpora:
            print(f"We found id [{corpus.id}] with name [{corpus.name}]")

    #@unittest.skip("This method appears to have not been implemented")
    def testReadCorpus(self):

        corpus = self.adminService.read_corpus(6)

        print("We found corpus [{corpus.}]")


