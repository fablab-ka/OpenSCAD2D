from src import cadfileparser

__author__ = 'sven'


class ArgumentParser(object):
    def __init__(self, primitive_name, termResolver, argument_definitions):
        self.primitive_name = primitive_name
        self.argument_definitions = argument_definitions
        self.termResolver = termResolver

        self.required_arguments = filter(lambda a: not a["optional"], self.argument_definitions)

        self.arguments_by_identifier = {}

        for a in self.argument_definitions:
            for name in a["names"]:
                self.arguments_by_identifier[name] = a

        self.docu_link = "https://github.com/fablab-ka/OpenSCAD2D"

    def create_docu_clue(self, target):
        target = '#' + target
        return "see documentation (" + self.docu_link + target + ")"

    def extract_assignments(self, arguments):
        assignments = []

        for a in arguments:
            if isinstance(a, cadfileparser.Assignment):
                assignments.append(a)
            else:
                raise Exception("You can either use Assignments or Arguments e.g. circle(r=1); or circle(1); not both")

        return assignments

    def resolve_value(self, value, types=None):
        if isinstance(value, float) or isinstance(value, long) or isinstance(value, bool):
            result = value
        elif isinstance(value, cadfileparser.BoolOperand):
            result = value.value
        elif isinstance(value, cadfileparser.Constant):
            if types is not None and not (value.type in types):
                raise Exception("Invalid type (" + value.type + ") of Constant (" + value.value + ") expected " + ", ".join(types))

            if isinstance(value.value, float) or isinstance(value, long) or isinstance(value, bool):
                result = value.value
            elif isinstance(value.value, str):
                result = float(value.value)
            else:
                raise Exception("Unknown type (" + value.type + ") of Constant (" + value.value + ")")
        elif isinstance(value, cadfileparser.UnresolvedCalculation):
            result = self.termResolver.calculate(value)
        elif isinstance(value, cadfileparser.Variable):
            result = self.termResolver.lookup_variable_value(value)
        elif isinstance(value, list):
            if len(value) == 0:
                result = None
                print("WARNING: non-value found")
            elif len(value) > 1:
                raise Exception("multiple values found")
            elif isinstance(value[0], cadfileparser.Variable):
                #todo lookup current value of: value[0].identifier
                result = -1
            else:
                raise Exception("Unknown Value type (" + str(type(value[0])) + ")")
        else:
            raise Exception("Unknown Value type (" + str(type(value)) + ")")

        return result

    def parse(self, arguments):
        result = [definition["default"] for definition in self.argument_definitions]

        if len(arguments) > len(self.argument_definitions) or len(arguments) <= 0:
            raise Exception("wrong number of arguments for circle." + self.create_docu_clue("Circle"))

        if all(map(lambda a: isinstance(a, cadfileparser.Assignment), arguments)):
            assignments = self.extract_assignments(arguments)

            for a in assignments:
                if a.identifier not in self.arguments_by_identifier.keys():
                    raise Exception("Unknown argument '" + a.identifier + "' for " + self.primitive_name + "." + self.create_docu_clue("Circle"))

                definition = self.arguments_by_identifier[a.identifier]

                result[definition["index"]] = self.resolve_value(a.value)
        else:
            if any(map(lambda a: isinstance(a, cadfileparser.Assignment), arguments)):
                raise Exception("You can either use Assignments or Arguments e.g. circle(r=1); or circle(1); not both")

            for i in range(len(arguments)):
                result[i] = self.resolve_value(arguments[i], self.argument_definitions[i]["types"])

        return result