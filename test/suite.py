import unittest
import test.test_manager as test_manager

class MyTestCase(unittest.TestCase):


    def test_integration(self):
        loader = unittest.TestLoader()
        my_suite = loader.loadTestsFromModule(test_manager)
        runner = unittest.TextTestRunner()
        runner.run(my_suite)



if __name__ == '__main__':
    unittest.main()
