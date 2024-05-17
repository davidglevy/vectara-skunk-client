from test.base import BaseClientTest
from pathlib import Path
import os

class IndexServiceIntegrationTest(BaseClientTest):

    def setUp(self, *args, **kwargs):
        super().setUp()

    def testUpload(self):
        # TODO Expand these integration tests with more cases.

        path = Path("resources/sigmod_photon.pdf")
        self.indexer_service.upload(self.corpus_id, path=path)





