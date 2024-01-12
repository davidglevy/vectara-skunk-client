import unittest


class MyTestCase(unittest.TestCase):
    def test_split(self):
        input = "david@vectara_client.com"
        expected = "david"
        result = input.split("@")[0][:10]
        self.assertEqual(expected, result)  # add assertion here


if __name__ == '__main__':
    unittest.main()
