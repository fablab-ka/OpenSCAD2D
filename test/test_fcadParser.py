import os
from src.cadfileparser import FcadParser

import unittest


class TestFcadParser(unittest.TestCase):
    pass

def create_parse_test(file):
    def test(self):
        filename = os.path.abspath(path + file)
        print ' ==== Next Test: ', file, ' ===='
        parser = FcadParser(filename)
        self.assertTrue(parser.program)

        result, error = parser.parse()

        if error:
            self.fail(error)
    return test

path = '../test/data/'
for file in os.listdir(path):
    test_name = 'test %s' % file
    test = create_parse_test(file)
    setattr(TestFcadParser, test_name, test)