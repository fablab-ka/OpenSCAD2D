from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QPolygonF
from shapely import affinity
from shapely.geometry import Point
import cadfileparser

class ArgumentParser:
    def __init__(self, primitive_name, argument_definitions):
        self.primitive_name = primitive_name
        self.argument_definitions = argument_definitions

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
        result = None

        if isinstance(value, cadfileparser.Constant):
            if types != None and not (value.type in types):
                raise Exception("Invalid type (" + value.type + ") of Constant (" + value.value + ") expected " + ", ".join(types))

            if value.type == 'INT':
                result = int(value.value)
            #TODO more types
            else:
                raise Exception("Unknown type (" + value.type + ") of Constant (" + value.value + ")")
        elif isinstance(value, cadfileparser.Variable):
            #todo lookup current value of: value[0].identifier
            result = -1
        elif isinstance(value, list):
            if len(value) == 0:
                result = None
                print "WARNING: non-value found"
            elif len(value) > 1:
                raise Exception("multiple values found")
            elif isinstance(value[0], cadfileparser.Variable):
                #todo lookup current value of: value[0].identifier
                result = -1
            else:
                raise Exception("Unknown type Value (" + repr(value[0]) + ")")
        else:
            raise Exception("Unknown type Value (" + repr(value) + ")")

        return result

    def parse(self, arguments):
        result = [definition["default"] for definition in self.argument_definitions]

        if len(arguments) > len(self.argument_definitions) or len(arguments) <= 0:
            raise Exception("wrong number of arguments for circle." + self.create_docu_clue("Circle"))

        if all(map(lambda a: isinstance(a, cadfileparser.Assignment), arguments)):
            assignments = self.extract_assignments(arguments)

            for a in assignments:
                if not a.identifier in self.arguments_by_identifier.keys():
                    raise Exception("Unknown argument '" + a.identifier + "' for " + self.primitive_name + "." + self.create_docu_clue("Circle"))

                definition = self.arguments_by_identifier[a.identifier]

                result[definition["index"]] = self.resolve_value(a.value)
        else:
            if any(map(lambda a: isinstance(a, cadfileparser.Assignment), arguments)):
                raise Exception("You can either use Assignments or Arguments e.g. circle(r=1); or circle(1); not both")

            for i in range(len(arguments)):
                result[i] = self.resolve_value(arguments[i], self.argument_definitions[i]["types"])

        return result

class GeometryGenerator:
    def __init__(self, screen_width, screen_height):
        self.default_resolution = 64

        self.current_position = [0.0, 0.0]
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.circle_argument_parser = ArgumentParser("circle", [{
            "names": ["r", "radius"],
            "types": ["INT"],
            "default": 1,
            "optional": False,
            "index": 0
        },{
            "names": ["fn$", "resolution"],
            "types": ["INT"],
            "default": self.default_resolution,
            "optional": True,
            "index": 1
        }])

    def create_circle(self, arguments):
        radius, resolution = self.circle_argument_parser.parse(arguments)

        return Point(self.current_position[0], self.current_position[1]).buffer(radius, resolution).exterior

    def create_primitive(self, primitive):
        result = None
        if primitive.name == "circle":
            result = self.create_circle(primitive.arguments)
        else:
            #todo proper error handling
            raise Exception("invalid primitive name '" + primitive.name + "'")

        return result

    def create_union(self, elements):
        #todo
        return elements[0]

    def generate(self, ast):
        result = []
        for statement in ast:
            if statement == cadfileparser.StatementType.NOP:
                pass
            elif isinstance(statement, cadfileparser.Statement) and statement.type == cadfileparser.StatementType.Primitive:
                result.append(self.create_primitive(statement))
            else:
                raise Exception("unknown statement " + repr(statement))

        if len(result) > 1:
            result = self.create_union(result)
        elif len(result) == 1:
            result = result[0]
        else:
            result = None

        result = affinity.translate(result, self.screen_width/2, self.screen_height/2)
        result = QPolygonF(map(lambda c: QPointF(c[0], c[1]), list(result.coords)))
        return result