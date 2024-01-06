import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        my_val = None
        self.assertFalse(my_val == True)
        self.assertFalse(my_val)
        self.assertTrue(my_val is None)

        my_val = True
        self.assertTrue(my_val == True)
        self.assertTrue(my_val)
        self.assertTrue(not my_val is None)
        self.assertTrue(my_val is not None)

        my_val = False
        self.assertFalse(my_val == True)
        self.assertFalse(my_val)
        self.assertFalse(my_val is None)

if __name__ == '__main__':
    unittest.main()
