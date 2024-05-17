from vectara_client.core import Factory
import logging

def cleanup():

    logging.basicConfig(format='%(asctime)s:%(name)-35s %(levelname)s:%(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S %z')

    logger = logging.getLogger(__name__)

    client = Factory().build()
    corpora = client.admin_service.list_corpora("test")
    for corpus in corpora:
        if "twitter" in corpus.name.lower():
            logger.info(f"Will not delete twitter corpus [{corpus.name}]")
        else:
            logger.info(f"We will delete corpus [{corpus.name}] with id [{corpus.id}]")
            client.admin_service.delete_corpus(corpus.id)


if __name__ == "__main__":
    cleanup()

