from test.base import BaseClientTest
import os


# TODO Add in common base test
class IndexServiceIntegrationTest(BaseClientTest):

    def setUp(self, *args, **kwargs):
        super().setUp()


    def testUpload(self):

        path = os.sep.join([".", "resources", "sigmod_photon.pdf"])
        indexer_service = self.indexer_service

        indexer_service.upload(6, path=path)

    def testUpload2(self):

        path = os.sep.join([".", "resources", "sigmod_photon.pdf"])
        indexer_service = self.indexer_service

        indexer_service.upload_old(6, path=path)




