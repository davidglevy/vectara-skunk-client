from test.base import BaseClientTest
from vectara_client.admin import CorpusBuilder
from vectara_client.domain import FilterAttributeType, FilterAttributeLevel


class AdminServiceIntTest(BaseClientTest):

    # def setUp(self):
    #    super().setUp()

    def testListCorpora(self):
        corpora = self.admin_service.list_corpora()
        for corpus in corpora:
            print(f"We found id [{corpus.id}] with name [{corpus.name}]")

        #    #@unittest.skip("This method appears to have not been implemented")
        #    def testReadCorpus(self):
        #
        #        corpus = self.adminService.read_corpus(6)

        print("We found corpus [{corpus.}]")

    # TODO Move this into document_test
    def testListDocuments(self):
        self.document_service.list_documents(self.corpus_id)

    def test_corpus_builder(self):
        builder = CorpusBuilder("test_car_corpus")

        # First attribute: using defaults for indexing and color
        request = (builder.description("This is a test corpus")
                   .add_attribute("color", "This is the color of the car")
                   .add_attribute("make", "The manufacturer of the car", indexed=True)
                   .add_attribute("author", "The author of the document", indexed=False)
                   .add_attribute("category", "The category of the section", document=False)
                   .add_attribute("year", "The year of manufacture", type="integer")
                   .build())

        corpus_id = self.admin_service.create_corpus_d(request).corpusId

        corpus = self.admin_service.read_corpus(corpus_id).corpus

        self.assertEqual(corpus.name, "test_car_corpus")
        self.assertEqual(corpus.description, "This is a test corpus")

        for filter_attr in corpus.filterAttributes:

            if filter_attr.name == "color":
                self.assertEqual(filter_attr.description, "This is the color of the car")
                self.assertEqual(filter_attr.indexed, True)
                self.assertEqual(filter_attr.type, FilterAttributeType.FILTER_ATTRIBUTE_TYPE__TEXT)
                self.assertEqual(filter_attr.level, FilterAttributeLevel.FILTER_ATTRIBUTE_LEVEL__DOCUMENT)
            elif filter_attr.name == "make":
                # Test that explicit index is true
                self.assertTrue(filter_attr.indexed)
            elif filter_attr.name == "author":
                # Test that explicit index is true
                self.assertFalse(filter_attr.indexed)
            elif filter_attr.name == "category":
                # Test that explicit index is true
                self.assertEqual(filter_attr.level, FilterAttributeLevel.FILTER_ATTRIBUTE_LEVEL__DOCUMENT_PART)
            elif filter_attr.name == "year":
                self.assertEqual(filter_attr.type, FilterAttributeType.FILTER_ATTRIBUTE_TYPE__INTEGER)
            else:
                self.fail(f"Unexpected filter attribute defined [{filter_attr.name}]")





