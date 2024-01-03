from vectara.core import Factory
from vectara.domain import Attribute
from typing import List
from unittest import TestCase
import logging
import os

logging.basicConfig(format='%(asctime)s %(name)-20s %(levelname)s:%(message)s', level=logging.INFO,
                    datefmt='%H:%M:%S %z')

logging.getLogger('OAuthUtil').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def create_test_corpus(test_name: str, username_prefix=True, quiet=False, recreate=False):
    if not test_name:
        raise TypeError("You must supply a test name")
    elif len(test_name) < 10:
        raise TypeError("Please use a descriptive name of at least 10 characters")

    if quiet:
        logging.getLogger('HomeConfigLoader').setLevel(logging.WARNING)
        logging.getLogger('RequestUtil').setLevel(logging.WARNING)

    username = os.getlogin()
    # Use maximum 10 characters from username
    user_part = username.split("@")[0][:10]
    logger.info(f"User prefix for test: {user_part}")

    full_test_name = f"{user_part}-{test_name}"
    logger.info(f"Setting up test corpus with name [{full_test_name}]")

    client = Factory().build()
    admin_service = client.admin_service

    corpora = admin_service.list_corpora(full_test_name)

    if len(corpora) >= 1:
        if recreate:
            for corpus in corpora:
                admin_service.delete_corpus(corpus.id)
        else:
            return corpora[0].id, True
    else:
        logging.info(f"No existing corpus with the name {full_test_name}")

    create_corpus_result = admin_service.create_corpus(full_test_name, description="Test Corpus")
    logging.info(f"New corpus created {create_corpus_result}")
    corpus_id = create_corpus_result.corpusId

    logger.info(f"New test created with id [{corpus_id}]")
    return corpus_id, False


def check_metadata(test: TestCase, expected: dict, result: List[Attribute]):
    for key in expected.keys():
        expected_value = expected[key]
        found = False
        result_value = None
        for attr in result:
            if attr.name == key:
                found = True
                result_value = attr.value
                break
        # First check attribute was found
        test.assertTrue(found, f"We did not find expected metadata in response with name [{key}]")

        # Next, check attribute had expected value
        test.assertEqual(expected_value, result_value, f"We were expecting a metadata attribute [{key}] with "
                                                        f"value [{expected_value}] but found [{result_value}]")