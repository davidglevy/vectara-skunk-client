import logging
from vectara_client.config import JsonConfigLoader, PathConfigLoader, HomeConfigLoader
from vectara_client.authn import OAuthUtil, ApiKeyUtil
from vectara_client.admin import AdminService
from vectara_client.document import DocumentService
from vectara_client.index import IndexerService
from vectara_client.query import QueryService
from vectara_client.util import RequestUtil
from vectara_client.corpus import CorpusManager


class Client:

    def __init__(self, customer_id: str, admin_service: AdminService,
                 indexer_service: IndexerService, query_service: QueryService,
                 document_service: DocumentService,
                 request_util: RequestUtil, corpus_manager: CorpusManager):
        self.logging = logging.getLogger(self.__class__.__name__)
        logging.info("initializing Client")
        self.customer_id = customer_id
        self.admin_service = admin_service
        self.indexer_service = indexer_service
        self.query_service = query_service
        self.document_service = document_service
        self.request_util = request_util
        self.corpus_manager = corpus_manager

    def get_requests(self):
        return self.request_util.requests

class Factory():

    def __init__(self, config_path: str = None, config_json: str = None, profile: str = None):
        """
        Initialize our factory using configuration which may either be in a file or serialized in a JSON string

        :param config_path: the file containing our configuration
        :param config_json: the JSON containing our configuration
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("initializing builder")
        self.config_path = config_path
        self.config_json = config_json
        self.profile = profile

    def build(self) -> Client:
        """
        Builds our client using the configuration which .
        :return:
        """

        # 1. Load the config whether we're doing file or we've had it passed in as a String.
        if self.config_path:
            self.logger.info("Factory will load configuration from path")
            config_loader = PathConfigLoader(config_path=self.config_path, profile=self.profile)
        elif self.config_json:
            self.logger.info("Factory will load configuration from JSON")
            config_loader = JsonConfigLoader(config_json=self.config_json, profile=self.profile)
        else:
            self.logger.info("Factory will load configuration from home directory")
            config_loader = HomeConfigLoader(profile=self.profile)

        # 2. Parse and validate the client configuration
        try:
            client_config = config_loader.load()
        except Exception as e:
            # Raise a new exception without extra stack trace. We know the JSON failed to parse.
            raise TypeError(f"Unable to build factory due to configuration error: {e}")

        errors = client_config.validate()
        if errors:
            raise TypeError(f"Client configuration is not valid {errors}")

        # 3. Load the validated configuration into our client.
        auth_config = client_config.auth
        auth_type = auth_config.getAuthType()
        logging.info(f"We are processing authentication type [{auth_type}]")

        if auth_type == "ApiKey":
            auth_util = ApiKeyUtil(client_config.customer_id, client_config.auth.api_key)
        elif auth_type == "OAuth2":
            auth_util = OAuthUtil(auth_config.auth_url, auth_config.app_client_id, auth_config.app_client_secret,
                                  client_config.customer_id)
        else:
            raise TypeError(f"Unknown authentication type: {auth_type}")

        # TODO Use the type of authentication to validate whether we can enabled the admin service.
        request_util = RequestUtil(auth_util)

        admin_service = AdminService(request_util, int(client_config.customer_id))
        indexer_service = IndexerService(auth_util, request_util, int(client_config.customer_id))
        query_service = QueryService(request_util, int(client_config.customer_id))
        document_service = DocumentService(request_util)
        corpus_manager = CorpusManager(admin_service, indexer_service)

        return Client(client_config.customer_id, admin_service, indexer_service, query_service, document_service,
                      request_util, corpus_manager)
