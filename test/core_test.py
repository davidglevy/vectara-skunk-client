import unittest
import logging
from vectara.client.core import Factory

logging.basicConfig(
        format=logging.BASIC_FORMAT, level=logging.INFO)


class FactoryTest(unittest.TestCase):


    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.logger = logging.getLogger(__class__.__name__)

    def testBuildValid(self):
        customer_id = "12344"
        api_key = "BLAH_KEY"

        config_json = f"""{{
                    "customer_id" : "{customer_id}",
                    "auth" : {{
                        "api_key" : "{api_key}"
                    }}
                }}"""


        factory = Factory(config_json=config_json)

        client = factory.build()

    def testBuildInvalidJson(self):
        api_key = "BLAH_KEY"

        # JSON has missing comma after customer Id.
        config_json = f"""{{
                    "customer_id" : ""
                    "auth" : {{
                        "api_key" : "{api_key}"
                    }}
                }}"""

        factory = Factory(config_json=config_json)

        with self.assertRaises(TypeError) as cm:
            client = factory.build()

        message = str(cm.exception)
        self.assertIn("Expecting ',' delimiter", message)


    def testBuildInvalidNoClientId(self):
        api_key = "BLAH_KEY"

        config_json = f"""{{
                    "auth" : {{
                        "api_key" : "{api_key}"
                    }}
                }}"""

        factory = Factory(config_json=config_json)

        with self.assertRaises(TypeError) as cm:
            client = factory.build()

        message = str(cm.exception)
        self.assertIn('missing value for field "customer_id"', message)


    def testBuildInvalidEmptyClientId(self):
        api_key = "BLAH_KEY"

        config_json = f"""{{
                    "customer_id" : "",
                    "auth" : {{
                        "api_key" : "{api_key}"
                    }}
                }}"""
        factory = Factory(config_json=config_json)

        with self.assertRaises(TypeError) as cm:
            client = factory.build()

        message = str(cm.exception)
        self.assertIn('You must define the field [customer_id]', message)


