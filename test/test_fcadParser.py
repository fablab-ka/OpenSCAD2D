import os
from src.cadfileparser import FcadParser

import unittest


class TestFcadParser(unittest.TestCase):
    def test_primitive_assignment(self):
        filename = os.path.abspath('../test/data/primitive.fcad')
        print '\n\n ============   clean primitive calls   ============'
        parser = FcadParser(filename)
        self.assertTrue(parser.program)

        result, error = parser.parse()

        if error: self.fail(error)

        self.assertTrue(len(result) == 2)
        self.assertTrue(result[0]['type'] == 'primitive', "unexpected token type '" + result[0]['type'] + "'")
        self.assertTrue(result[0]['name'] == 'circle', "unexpected token name '" + result[0]['name'] + "'")
        self.assertTrue(result[0]['arguments'][0] == 'r', "unexpected argument '" + result[0]['arguments'][0] + "'")
        self.assertTrue(result[0]['arguments'][1] == '1', "unexpected argument '" + result[0]['arguments'][1] + "'")

        self.assertTrue(result[1]['type'] == 'primitive', "unexpected token type '" + result[1]['type'] + "'")
        self.assertTrue(result[1]['name'] == 'circle', "unexpected token name '" + result[1]['name'] + "'")
        self.assertTrue(result[1]['arguments'][0] == '2', "unexpected argument '" + result[1]['arguments'][0] + "'")

def create_parse_test(path, file):
    def test(self):
        filename = os.path.abspath(path + file)
        print '\n\n ============   ', file, '   ============'
        parser = FcadParser(filename)
        self.assertTrue(parser.program)

        result, error = parser.parse()

        if error: self.fail(error)
    return test

path = '../test/data/'
for file in os.listdir(path):
    test_name = 'test %s' % file
    test = create_parse_test(path, file)
    setattr(TestFcadParser, test_name, test)