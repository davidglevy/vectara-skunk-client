import unittest
import logging
from vectara.core import Factory
import json
import os
from test.base import BaseClientTest
from vectara.util import render_markdown

import os

class QueryIntegrationTest(BaseClientTest):


    def test_query_corpora(self):
        """
        Run a test over corpora - using Photon paper.

        TODO Make the corpora id dynamic and refreshed by a "start" test.
        :return:
        """
        qs = self.client.query_service
        query = "At Vectara, Can I bring any birds to the Vectara Office?"
        #query = "هل يمكنني إحضار أي طيور إلى مكتب Vectara؟"
        response = qs.query(query, 126)
        self.logger.info(render_markdown(query, response))