from __future__ import print_function
import os
from src.cadfileparser import FcadParser, StatementType, Statement, Assignment, Constant

import unittest

file_dir = os.path.dirname(os.path.realpath(__file__))

class TestFcadParser(unittest.TestCase):
    def test_primitive_assignment(self):
        filename = os.path.abspath(file_dir + '/../test/data/primitive.fcad')
        print('\n\n ============   clean primitive calls   ============')
        parser = FcadParser(filename)
        self.assertTrue(parser.program)

        result, error = parser.parse()

        if error: self.fail(error)

        self.assertTrue(result[0].type == StatementType.Primitive, "unexpected token type '" + result[0].type + "'")
        self.assertTrue(result[0].name == 'circle', "unexpected token name '" + result[0].name + "'")
        self.assertTrue(isinstance(result[0].arguments[0], Assignment), "unexpected argument type")
        self.assertTrue(result[0].arguments[0].identifier == 'r', "unexpected argument '" + result[0].arguments[0].identifier + "'")
        self.assertTrue(isinstance(result[0].arguments[0].value, Constant), "unexpected argument value type")
        self.assertTrue(result[0].arguments[0].value.type == 'INT', "unexpected argument value type'" + str(result[0].arguments[0].value.type) + "'")

        self.assertTrue(result[1].type == StatementType.Primitive, "unexpected token type '" + result[1].type + "'")
        self.assertTrue(result[1].name == 'circle', "unexpected token name '" + result[1].name + "'")
        self.assertTrue(result[1].arguments[0].value == '2', "unexpected argument value '" + str(result[1].arguments[0].value) + "'")
        self.assertTrue(result[1].arguments[0].type == 'INT', "unexpected argument value '" + str(result[1].arguments[0].type) + "'")

        # todo test last statements

def create_parse_test(path, file):
    def test(self):
        filename = os.path.abspath(path + file)
        print('\n\n ============   ', file, '   ============')
        parser = FcadParser(filename)
        self.assertTrue(parser.program)

        result, error = parser.parse()

        if error: self.fail(error)
    return test

path = file_dir + '/../test/data/'
for file in os.listdir(path):
    test_name = 'test %s' % file
    test = create_parse_test(path, file)
    setattr(TestFcadParser, test_name, test)

if __name__ == '__main__':
    unittest.main()