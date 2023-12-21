import logging
from typing import List
from vectara.core import Client
from vectara.dao import ManagerDao, CorpusDao
from vectara.admin import AdminService

class VectaraManager():

    def __init__(self,client:Client, dao:ManagerDao, corpusDao:CorpusDao, adminService:AdminService):
        self.logger = logging.getLogger(__class__.__name__)
        self.client = client
        self.dao = dao
        self.corpusDao = corpusDao
        self.adminService = adminService
    """
    Provides a method to perform higher level operations against multiple corpus
    """

    def sync_local_db(self):
        """
        Synchronize our local database with the corpora found in the account.

        TODO Synchronize the documents in the corpus too.
        :return:
        """
        corpora = self.adminService.list_corpora()
        for corpus in corpora:
            self.logger.info(f"Found {corpus.name}")
            self.corpusDao.registerCorpus(corpus)


    def promote(self, corpus_id: int, document_ids: List[str], release_tag:str):
        """
        Promote the documents with the given ids to the specified corpus.

        :param corpus_id:
        :param document_ids:
        :return:
        """

    def addQuestion(self, question:str, tags:List[str] = None) -> int:
        """
        Add the question to our regression suite

        :param tags:
        :param question:
        :return:
        """


    def runRegressionCycle(self, corpus_ids: List[int], question_tags:List[str]):
        pass