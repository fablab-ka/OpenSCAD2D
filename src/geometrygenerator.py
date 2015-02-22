from shapely import affinity
from shapely.geometry import Point
import cadfileparser


class GeometryGenerator:
    def __init__(self, screen_width, screen_height):
        self.default_resolution = 64
        self.docu_link = "https://github.com/fablab-ka/OpenSCAD2D"

        self.current_position = [0.0, 0.0]
        self.screen_width = screen_width
        self.screen_height = screen_height

    def create_docu_clue(self, target):
        target = '#' + target
        return "see documentation (" + self.docu_link + target + ")"

    def extract_assigments(self, arguments):
        assignments = []

        for a in arguments:
            if isinstance(a, cadfileparser.Assignment):
                assignments.append(a)
            else:
                raise Exception("You can either use Assignments or Arguments e.g. circle(r=1); or circle(1); not both")

        return assignments

    def resolve_value(self, value):
        result = None

        if isinstance(value, cadfileparser.Constant):
            if value.type == 'INT':
                result = int(value.value)
            else:
                raise Exception("Unknown type (" + value.type + ") of Constant (" + value.identifier + ")")
        elif isinstance(value, cadfileparser.Variable):
            #todo lookup current value of: value[0].identifier
            result = -1
        elif isinstance(value, list):
            if len(value) == 0:
                result = None
                print "WARNING: non-value found"
            elif len(value) > 1:
                raise "multiple valuata found"
            elif isinstance(value[0], cadfileparser.Variable):
                #todo lookup current value of: value[0].identifier
                result = -1
            else:
                raise Exception("Unknown type Value (" + repr(value[0]) + ")")
        else:
            raise Exception("Unknown type Value (" + repr(value) + ")")

        return result

    def create_circle(self, arguments):
        radius = 1
        resolution = self.default_resolution

        if len(arguments) > 2 or len(arguments) <= 0:
            raise Exception("wrong number of arguments for circle." + self.create_docu_clue("Circle"))

        if len(arguments) == 1 and not isinstance(arguments[0], cadfileparser.Assignment):
            radius = self.resolve_value(arguments[0])
        elif len(arguments) == 2 and not isinstance(arguments[0], cadfileparser.Assignment)\
             and not isinstance(arguments[1], cadfileparser.Assignment):
            radius = self.resolve_value(arguments[0].value)
            resolution = self.resolve_value(arguments[1].value)
        else:
            assignments = self.extract_assigments(arguments)

            for a in assignments:
                if a.identifier == "$fn":
                    resolution = self.resolve_value(a.value)
                elif a.identifier == "r":
                    radius = self.resolve_value(a.value)
                else:
                    raise Exception("invalid argument for circle." + self.create_docu_clue("Circle"))

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

        return result