from test.base import BaseClientTest


class AdminServiceIntTest(BaseClientTest):

    #def setUp(self):
    #    super().setUp()

    def testListCorpora(self):
        corpora = self.adminService.list_corpora()
        for corpus in corpora:
            print(f"We found id [{corpus.id}] with name [{corpus.name}]")

#    #@unittest.skip("This method appears to have not been implemented")
#    def testReadCorpus(self):
#
#        corpus = self.adminService.read_corpus(6)

        print("We found corpus [{corpus.}]")

    def testListDocuments(self):
        self.admin_service.list_documents(6)



