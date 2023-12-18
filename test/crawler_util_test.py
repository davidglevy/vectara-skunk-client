import unittest
from vectara.cralwer_util import CrawlerUtil, JwtAuthenticator
import yaml
import logging

INDEXER_HOST = "api.vectara.io"

logging.basicConfig(
        format=logging.BASIC_FORMAT, level=logging.INFO)

def loadTestConfig():
    with open(".vectara_test_config", "r") as yaml_stream:
        print("Loading test credentials")
        creds = yaml.safe_load(yaml_stream)
        return creds


class JwtAuthenticatorTest(unittest.TestCase):

    def setUp(self):
        creds = loadTestConfig()
        default_auth = creds["default"]
        # This is what occurs when no
        self.auth_url = default_auth["auth_url"]
        self.app_client_id = default_auth["app_client_id"]
        self.app_client_secret = default_auth["app_client_secret"]
        self.customer_id = default_auth["customer_id"]

    def testAuthenticateNoUrl(self):
            self.focus = JwtAuthenticator("", self.app_client_id, self.app_client_secret, self.customer_id)
            self.focus.authenticate()


    def testAuthenticateNoUrlAndNoClientId(self):

        with self.assertRaises(TypeError) as cm:
            self.focus = JwtAuthenticator("", self.app_client_id, self.app_client_secret, "")

        message = str(cm.exception)
        self.assertIn('You must either put in a client Id or OAuth authentication URL', message)

    def testAuthenticateNoAppClientId(self):
        with self.assertRaises(TypeError) as cm:

            self.focus = JwtAuthenticator("", "", self.app_client_secret, self.customer_id)
        message = str(cm.exception)
        self.assertIn('You must include an application client Id', message)

    def testGetToken(self):
        self.focus = JwtAuthenticator("", self.app_client_id, self.app_client_secret, self.customer_id)
        self.focus.authenticate()

        token = self.focus.getToken()
        self.assertTrue(len(token) > 0)


class CrawlerUtilTest(unittest.TestCase):

    def setUp(self):
        self.focus = CrawlerUtil()

    def test_with_port(self):
        print("Hello")
        test_url_1 = "https://www.github.com:443/my/path"
        result = self.focus.convertUrlToFile(test_url_1)
        expected_file_name_1 = "www-github-com_my-path.1.pdf"
        self.assertEqual(expected_file_name_1, result)


    def test_with_params(self):
        test_url = "https://www.github.com:443/my/path?param1=hello&param2=world"
        result = self.focus.convertUrlToFile(test_url)
        expected_file_name = "www-github-com_my-path_param1-hello_param2-world.1.pdf"
        self.assertEqual(expected_file_name, result)

    def test_names_unique(self):
        print("Hello")
        test_url_1 = "https://www.github.com:443/my/path"
        result_1 = self.focus.convertUrlToFile(test_url_1)
        expected_file_name_1 = "www-github-com_my-path.1.pdf"
        self.assertEqual(expected_file_name_1, result_1)


        test_url_2 = "https://www.github.com:443/my/path"
        result_2 = self.focus.convertUrlToFile(test_url_2)
        expected_file_name_2 = "www-github-com_my-path.2.pdf"
        self.assertEqual(expected_file_name_2, result_2)
