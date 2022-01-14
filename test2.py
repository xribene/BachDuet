import unittest

class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("setUpClass")

    def setUp(self):
        print("setUp")

    def test1(self):
        print("test1")

    def test2(self):
        print("test2")

    def tearDown(self):
        print("tearDown")
    
    

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()