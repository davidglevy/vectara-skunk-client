from unittest import TestCase, SkipTest
from vectara_client.dao import CoreDao, ManagerDao


class CoreDaoTest(TestCase):

    @SkipTest
    def testSetupDatbase(self):

        dao = CoreDao()
        dao.setupDatabase()

    @SkipTest
    def testDropDatabase(self):
        dao = CoreDao()
        dao.dropDatabase()

    def testBlah(self):
        pass

class ManagerDaoTest(TestCase):

    @SkipTest
    def testAddQuestion(self):
        dao = ManagerDao()
        result = dao.addQuestion("Why was the photon engine created?")
        print(result)