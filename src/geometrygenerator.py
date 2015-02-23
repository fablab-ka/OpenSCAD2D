from __future__ import print_function
from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QPolygonF
from shapely import affinity
from shapely.geometry import Point, LinearRing, MultiLineString, MultiPoint
from shapely.geometry.base import BaseMultipartGeometry
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
                print("WARNING: non-value found")
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
            "types": ["INT", "FLOAT"],
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

        self.rect_argument_parser = ArgumentParser("rect", [{
            "names": ["w", "width"],
            "types": ["INT", "FLOAT"],
            "default": 1,
            "optional": False,
            "index": 0
        },{
            "names": ["h", "height"],
            "types": ["INT", "FLOAT"],
            "default": 1,
            "optional": False,
            "index": 1
        }])

        self.translate_argument_parser = ArgumentParser("translate", [{
            "names": ["x"],
            "types": ["INT", "FLOAT"],
            "default": 0,
            "optional": False,
            "index": 0
        },{
            "names": ["y"],
            "types": ["INT", "FLOAT"],
            "default": 0,
            "optional": False,
            "index": 1
        }])

        self.rotate_argument_parser = ArgumentParser("rotate", [{
            "names": ["a", "angle"],
            "types": ["INT", "FLOAT"],
            "default": 0,
            "optional": False,
            "index": 0
        },{
            "names": ["x", "xorigin"],
            "types": ["INT", "FLOAT"],
            "default": None,
            "optional": True,
            "index": 1
        },{
            "names": ["y", "yorigin"],
            "types": ["INT", "FLOAT"],
            "default": None,
            "optional": True,
            "index": 2
        },{
            "names": ["rad", "use_radian"],
            "types": ["BOOLEAN"],
            "default": False,
            "optional": True,
            "index": 3
        }])

        self.scale_argument_parser = ArgumentParser("scale", [{
            "names": ["x"],
            "types": ["INT", "FLOAT"],
            "default": 0,
            "optional": False,
            "index": 0
        },{
            "names": ["y"],
            "types": ["INT", "FLOAT"],
            "default": 0,
            "optional": False,
            "index": 1
        }])

    def create_circle(self, arguments):
        radius, resolution = self.circle_argument_parser.parse(arguments)

        return Point(self.current_position[0], self.current_position[1]).buffer(radius, resolution)

    def create_rect(self, arguments):
        w, h = self.rect_argument_parser.parse(arguments)
        x, y = self.current_position
        return MultiPoint([(x, y), (x, y + h), (x + w, y + h), (x + w, y)]).convex_hull

    def create_primitive(self, primitive):
        result = None

        if primitive.name == "circle":
            result = self.create_circle(primitive.arguments)
        elif primitive.name == "rect":
            result = self.create_rect(primitive.arguments)
        else:
            raise Exception("invalid primitive name '" + primitive.name + "'")

        if primitive.modifiers:
            for modifier in primitive.modifiers:
                result = self.apply_modifier(result, modifier)

        return result

    def apply_translation(self, geom, translation):
        x, y = self.translate_argument_parser.parse(translation.arguments)
        return affinity.translate(geom, x, y)

    def apply_rotation(self, geom, translation):
        angle, origin_x, origin_y, use_radians = self.rotate_argument_parser.parse(translation.arguments)
        return affinity.rotate(geom, angle, Point(origin_x, origin_y), use_radians)

    def apply_scale(self, geom, translation):
        x, y = self.scale_argument_parser.parse(translation.arguments)
        return affinity.scale(geom, x, y)

    def apply_modifier(self, geom, modifier):
        result = geom

        if modifier.name == "translate":
            result = self.apply_translation(geom, modifier)
        elif modifier.name == "rotate":
            result = self.apply_rotation(geom, modifier)
        elif modifier.name == "scale":
            result = self.apply_scale(geom, modifier)
        else:
            raise Exception("Unknown Modifier '" + modifier.name + "'")

        return result

    def create_union(self, elements):
        result = elements[0]
        for elem in elements[1:]:
            result = result.union(elem)
        return result

    def generate(self, ast):
        self.current_position = [self.screen_width/2, self.screen_height/2]
        primitives = []
        for statement in ast:
            if statement == cadfileparser.StatementType.NOP:
                pass
            elif isinstance(statement, cadfileparser.Statement) and statement.type == cadfileparser.StatementType.Primitive:
                primitives.append(self.create_primitive(statement))
            else:
                raise Exception("unknown statement " + repr(statement))

        root_element = None
        if len(primitives) > 1:
            root_element = self.create_union(primitives)
        elif len(primitives) == 1:
            root_element = primitives[0]

        result = []
        if isinstance(root_element, BaseMultipartGeometry):
            for geom in root_element.geoms:
                result.append(QPolygonF(map(lambda c: QPointF(c[0], c[1]), list(geom.coords))))
        else:
            result = [QPolygonF(map(lambda c: QPointF(c[0], c[1]), list(root_element.exterior.coords)))]

        return result