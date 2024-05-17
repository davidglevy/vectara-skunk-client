import re
from urllib.parse import urlparse
import unittest
import requests
import logging
from authlib.integrations.requests_client import OAuth2Session
import datetime
import traceback
from abc import ABC

# TODO This should be discovered from the console
# TODO Change this file to authc.py!!
DEFAULT_OAUTH2_URL = "https://vectara-prod-{customer_id}.auth.us-west-2.amazoncognito.com/oauth2/token"

logger = logging.getLogger(__name__)


class BaseAuthUtil(ABC):

    def get_headers(self) -> dict:
        raise NotImplementedError("You must implement this on a subclass")

    def authenticate(self):
        pass

class OAuthUtil(BaseAuthUtil):

    def __init__(self, auth_url: str, app_client_id: str, app_client_secret: str, customer_id: str):
        self.logger = logging.getLogger(str(__class__.__name__))

        if not customer_id:
            # Putting this in as I'm surprised we also need a customer Id on the header.
            raise TypeError("You must include a customer Id, apparently?")
        else:
            self.customer_id = customer_id

        # Validate
        if not auth_url and not customer_id:
            raise TypeError("You must either put in a client Id or OAuth authentication URL")
        if not app_client_secret:
            raise TypeError("You must include an application client secret")
        if not app_client_id:
            raise TypeError("You must include an application client Id")



        if auth_url:
            self.logger.info(f"Using provided OAuth2 URL [{auth_url}]")
            self.auth_url = auth_url
        else:
            self.logger.info(f"No Authentication URL Provided for OAuth2, creating default from customer id [{customer_id}]")
            self.auth_url = (DEFAULT_OAUTH2_URL).format(customer_id=customer_id)
        self.logger.info(f"OAuth2 URL is [{self.auth_url}]")

        self.app_client_id = app_client_id
        if self.app_client_id:
            self.logger.debug(f"OAuth Application Client Id: {self.app_client_id}")
        self.app_client_secret = app_client_secret
        if self.app_client_secret:
            self.logger.debug(f"OAuth Application Client Secret: {self.app_client_secret}")

        self.expiry_ts = None
        self.expiry_txt = None
        self.expires_in = None
        self.expires_at = None
        self.access_token = None

    def authenticate(self):
        """Connect to the server and get a JWT token."""

#        try:
        session = OAuth2Session(
            self.app_client_id, self.app_client_secret, scope="")
        token = session.fetch_token(self.auth_url, grant_type="client_credentials")
        self.expires_at = token["expires_at"]
        self.expires_in = token["expires_in"]
        self.access_token = token["access_token"]

        self.expiry_ts = datetime.datetime.fromtimestamp(self.expires_at)
        self.expiry_txt = self.expiry_ts.strftime("%m/%d/%Y, %H:%M:%S")
        self.logger.info(f"Received OAuth token, will expire [{self.expiry_txt}]")

    def getToken(self):
        """Get the current token or get a new one if expired"""
        now = datetime.datetime.now()
        self.logger.info(f"Current timestamp {now}")

        if self.expiry_ts:
            self.logger.info(f"Expiry            {self.expiry_ts}")

        if not self.access_token:
            self.logger.info("First time requesting token, authenticating")
            self.authenticate()
        if (now > (self.expiry_ts - datetime.timedelta(seconds=5))):
            self.logger.info("Token expiry within 5 seconds, refreshing")
            self.authenticate()
        else:
            self.logger.info(f"Already authenticated with non-expired token, expiry is [{self.expires_at}]")

        return self.access_token

    def get_headers(self) -> dict:
        token = self.getToken()

        return {
            "Customer-Id": self.customer_id,
            "Authorization": f"Bearer {token}"
        }

class ApiKeyUtil(BaseAuthUtil):

    def __init__(self, customer_id, api_key):
        self.customer_id = customer_id
        self.api_key = api_key

    def get_headers(self):
        return {
            "customer-id": self.customer_id,
            "x-api-key": self.api_key
        }