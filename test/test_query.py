import unittest
import logging
from vectara.core import Factory
import json
import os
from test.base import BaseClientTest
from vectara.util import render_markdown

import os

class AdminServiceIntegrationTest(BaseClientTest):


    def test_query_corpora(self):
        """
        Run a test over corpora

        TODO Make the corpora id dynamic and refreshed by a "start" test.
        :return:
        """
        qs = self.client.query_service
        query = "Which state has the fastest internet speeds in Australia?"
        response = qs.query(query, 6)
        self.logger.info(render_markdown(query, response))