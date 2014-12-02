from cadfileparser import *


class SvgGenerator:
    def __init__(self, ast):
        self.ast = ast

    def generate(self):
        return "test"


if __name__ == "__main__":
    #if argument:
    parser = FcadParser("sample.fcad")
    ast = parser.parse()
    generator = SvgGenerator(ast)
    generator.generate()
    #else show UI

