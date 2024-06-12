from vectara_client.admin import AdminService
from vectara_client.index import IndexerService
from vectara_client.domain import Corpus, IndexDocument
from vectara_client.util import CountDownLatch
from typing import List, Union
from threading import Thread
import logging

class SubIndexer:
    """
        Class designed to be used inside a thread to run multiple indexing requests and track completions.
    """

    def __init__(self, indexer_service: IndexerService, corpus_id: int, latch: CountDownLatch, thread_index: int):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.indexer_service = indexer_service
        self.corpus_id = corpus_id
        self.latch = latch
        self.thread_index = thread_index

        self.docs = []
        self.results = []

    def add_doc(self, doc):
        self.docs.append(doc)

    def index_docs(self):
        # TODO Handle success and failure into results array
        self.logger.info(f"Worker [{self.thread_index}] Starting our [{len(self.docs)}] indexer requests")

        for doc in self.docs:
            try:
                result = self.indexer_service.index_doc(self.corpus_id, doc)

            except Exception as e:
                # Ignore for lab
                self.logger.error("Error: {e}")
        self.logger.info(f"Worker [{self.thread_index}] Finished our indexer requests")
        self.latch.count_down()

class SubCoreIndexer:
    """
        Class designed to be used inside a thread to run multiple indexing requests and track completions.
    """

    def __init__(self, indexer_service: IndexerService, corpus_id: int, latch: CountDownLatch, thread_index: int):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.indexer_service = indexer_service
        self.corpus_id = corpus_id
        self.latch = latch
        self.thread_index = thread_index

        self.docs = []
        self.results = []

    def add_doc(self, doc):
        self.docs.append(doc)

    def index_docs(self):
        # TODO Handle success and failure into results array
        self.logger.info(f"Worker [{self.thread_index}] Starting our [{len(self.docs)}] indexer requests")

        for doc in self.docs:
            try:
                result = self.indexer_service.index_core_doc(self.corpus_id, doc)
                self.results.append({"result": result})
            except Exception as e:
                # Ignore for lab
                self.logger.error(f"Error: {e}")
                self.results.append({"error": e})
        self.logger.info(f"Worker [{self.thread_index}] Finished our indexer requests")
        self.latch.count_down()

class CorpusManager:
    """
    Provides a layer of intelligence over the operations regarding corpus lifecycle.
    """

    admin_service: AdminService

    def __init__(self, admin_service: AdminService, indexer_service: IndexerService):
        self.logger = logging.getLogger(__class__.__name__)
        self.admin_service = admin_service
        self.indexer_service = indexer_service

    def find_corpora_by_name(self, name: str) -> List[int]:
        corpora = self.admin_service.list_corpora(name)

        found: List[int] = []
        for potential in corpora:
            self.logger.info(f"Checking corpus with name [{potential.name}]")
            if potential.name == name:
                found.append(potential.id)

        self.logger.info(f"We found the following corpora with name [{name}]: {found}")
        return found


    def find_corpus_by_name(self, name: str, fail_if_not_exist=True) -> int | None:
        corpora = self.admin_service.list_corpora(name)

        found = None
        for potential in corpora:
            self.logger.info(f"Checking corpus with name [{potential.name}]")
            if potential.name == name:
                if found:
                    raise Exception(f"We found multiple matching corpus with name [{name}]")
                else:
                    found = potential

        if not found:
            if fail_if_not_exist:
                raise Exception(f"We did not find a corpus matching [{name}]")
            else:
                self.logger.info("No corpus with name [" + name + "] can be found")
                return None
        else:
            corpus_id = found.id

        self.logger.info(f"Our corpus id is [{corpus_id}]")
        return corpus_id

    def delete_corpus_by_name(self, name: str) -> bool:
        self.logger.info(f"Deleting existing corpus named [{name}]")

        # The filter below will match any corpus with "verified-corpus" anywhere in the name, so we need a
        # client side check to validate equivalence.
        existing_corpora = self.admin_service.list_corpora(name)
        self.logger.info(f"We found [{len(existing_corpora)}] potential matches")
        found = False
        for existing_corpus in existing_corpora:
            if existing_corpus.name == name:
                # The following code will delete the corpus
                self.logger.info(f"Deleting existing corpus with id [{existing_corpus.id}]")
                self.admin_service.delete_corpus(existing_corpus.id)
                found = True
            else:
                self.logger.info(
                    f"Ignoring corpus with id [{existing_corpus.id}] as it doesn't match our target name exactly")
        return found

    def create_corpus(self, corpus:Corpus, delete_existing=False, unique=True) -> int:
        """
        Creates a new corpus with sensible defaults. Look at CorpusBuilder for a simplified notation
        to create a corpus.

        :param corpus: the new corpus to create.
        :param delete_existing: whether we delete an existing corpus with the same name.
        :param unique: whether we fail if there is an existing corpus of the same name.
        :return: the id of the new corpus.

        """
        self.logger.info(f"Performing account checks before corpus creation for name [{corpus.name}]")
        existing_ids = self.find_corpora_by_name(corpus.name)
        has_existing = len(existing_ids) > 0
        if has_existing:
            self.logger.info(f"We found existing corpus with name [{corpus.name}]")
            if delete_existing:
                self.delete_corpus_by_name(corpus.name)
            elif unique:
                raise Exception(f"Unable to create a corpus with the name [{corpus.name}] as there were existing ones and "
                                f"the flag \"delete_existing\" is \"False\".")
            else:
                self.logger.warning(f"There is a potential for confusion as there is already a corpus with name [{corpus.name}]")
        self.logger.info("Account checks complete, creating the new corpus")

        return self.admin_service.create_corpus_d(corpus).corpusId



    def batch_index(self, corpus_id:int, documents: List[Union[dict, IndexDocument]], threads:int=10) -> List[any]:
        self.logger.info(f"Performing parallel [{threads}] document indexing requests")

        # Create our countdown latch
        latch = CountDownLatch(threads)

        # Create sub-indexers for each thread
        sub_indexers = [ SubIndexer(self.indexer_service, corpus_id, latch, thread_index) for thread_index in range(threads)]

        for index, doc in enumerate(documents):
            thread_index = index % threads
            sub_indexers[thread_index].add_doc(doc)

        for sub_indexer in sub_indexers:
            thread = Thread(target=sub_indexer.index_docs)
            thread.start()

        # Wait for completion.
        latch.sweat_it_out()

        # TODO Extract results from each sub-indexer into a final result array and return it.

    def batch_core_index(self, corpus_id:int, documents: List[Union[dict, IndexDocument]],
                         threads: int = 10) -> List[any]:
        self.logger.info(f"Performing parallel [{threads}] document indexing requests")

        # Create our countdown latch
        latch = CountDownLatch(threads)

        # Create sub-indexers for each thread
        sub_indexers = [SubCoreIndexer(self.indexer_service, corpus_id, latch, thread_index)
                        for thread_index in range(threads)]

        for index, doc in enumerate(documents):
            thread_index = index % threads
            sub_indexers[thread_index].add_doc(doc)

        for sub_indexer in sub_indexers:
            thread = Thread(target=sub_indexer.index_docs)
            thread.start()

        # Wait for completion.
        latch.sweat_it_out()

        # TODO Extract results from each sub-indexer into a final result array and return it.


