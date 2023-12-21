from unittest import TestCase
from vectara.index import IndexerService
import logging
import os


# TODO Add in common base test
class IndexServiceIntegrationTest(TestCase):

    def setUp(self):
        self.target = IndexerService()

    def testUpload(self):
        path = os.sep.join([".", "resources", "sigmod_photon.pdf"])
        self.target.upload(path=path)




