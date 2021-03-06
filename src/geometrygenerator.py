from __future__ import print_function

from PySide.QtCore import QPointF
from PySide.QtGui import QPolygonF
from shapely import affinity
from shapely.geometry import Point, MultiPoint, Polygon
from shapely.geometry.base import BaseMultipartGeometry

from src import cadfileparser
from src.argumentparser import ArgumentParser
from src.unresolvedtermresolver import UnresolvedTermResolver


class GeometryGenerator(object):
    def __init__(self, screen_width, screen_height):
        self.default_resolution = 64

        self.current_position = [0.0, 0.0]
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.termResolver = UnresolvedTermResolver()

        self.circle_argument_parser = ArgumentParser("circle", self.termResolver, [{
            "names": ["r", "radius"],
            "types": ["INT", "FLOAT"],
            "default": 1,
            "optional": False,
            "index": 0
        },{
            "names": ["$fn", "fn$", "resolution"],
            "types": ["INT"],
            "default": self.default_resolution,
            "optional": True,
            "index": 1
        }])

        self.rect_argument_parser = ArgumentParser("rect", self.termResolver, [{
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

        self.translate_argument_parser = ArgumentParser("translate", self.termResolver, [{
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

        self.rotate_argument_parser = ArgumentParser("rotate", self.termResolver, [{
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

        self.scale_argument_parser = ArgumentParser("scale", self.termResolver, [{
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

        self.simplify_argument_parser = ArgumentParser("scale", self.termResolver, [{
            "names": ["t", "tolerance"],
            "types": ["INT", "FLOAT"],
            "default": 0.5,
            "optional": False,
            "index": 0
        },{
            "names": ["p", "preserve_topology"],
            "types": ["BOOLEAN"],
            "default": False,
            "optional": True,
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

    def apply_simplify(self, geom, translation):
        tolerance, preserve_topology = self.simplify_argument_parser.parse(translation.arguments)
        return geom.simplify(tolerance, preserve_topology)

    def apply_modifier(self, geom, modifier):
        result = geom

        if modifier.name == "translate":
            result = self.apply_translation(geom, modifier)
        elif modifier.name == "rotate":
            result = self.apply_rotation(geom, modifier)
        elif modifier.name == "scale":
            result = self.apply_scale(geom, modifier)
        elif modifier.name == "simplify":
            result = self.apply_simplify(geom, modifier)
        else:
            raise Exception("Unknown Modifier '" + modifier.name + "'")

        return result

    def create_union(self, elements):
        result = elements[0]
        for elem in elements[1:]:
            result = result.union(elem)
        return result

    def create_difference(self, elements):
        result = elements[0]
        for elem in elements[1:]:
            result = result.difference(elem)
        return result

    def create_intersection(self, elements):
        result = elements[0]
        for elem in elements[1:]:
            result = result.intersection(elem)
        return result

    def apply_temporary_assignments(self, scope):
        for assignment in scope.arguments:
            self.termResolver.assignment_stack.append(assignment)

    def resolve_temporary_assignments(self):
        self.termResolver.assignment_stack.pop()

    def being_scope(self, scope):
        if scope.name == "union":
            pass
        elif scope.name == "difference":
            pass
        elif scope.name == "intersection":
            pass
        elif scope.name == "combine":
            pass
        elif scope.name == "assign":
            self.apply_temporary_assignments(scope)
        else:
            raise Exception("Unknown Scope '" + scope.name + "'")

    def end_scope(self, scope, primitives):
        result = primitives

        if scope.name == "union":
            result = self.create_union(primitives)
        elif scope.name == "difference":
            result = self.create_difference(primitives)
        elif scope.name == "intersection":
            result = self.create_intersection(primitives)
        elif scope.name == "assign":
            self.resolve_temporary_assignments()
        else:
            raise Exception("Unknown Scope '" + scope.name + "'")

        return result

    def create_scope(self, scope):
        self.being_scope(scope)
        result = self.extract_primitives(scope.children)
        result = self.end_scope(scope, result)

        if scope.modifiers:
            for modifier in scope.modifiers:
                result = self.apply_modifier(result, modifier)

        return result

    def extract_primitives(self, expression_list):
        result = []

        for expression in expression_list:
            if isinstance(expression, cadfileparser.Statement) and expression.type == cadfileparser.StatementType.Primitive:
                result.append(self.create_primitive(expression))
            elif isinstance(expression, cadfileparser.Scope):
                scope_result = self.create_scope(expression)
                if isinstance(scope_result, list):
                    result.extend(scope_result)
                else:
                    result.append(scope_result)
            else:
                raise Exception("unknown expression type " + repr(type(expression)) + " ( " + repr(expression) + " )")

        return result

    def generate(self, ast):
        self.current_position = [self.screen_width/2, self.screen_height/2]

        primitives = self.extract_primitives(ast)

        root_element = None
        if len(primitives) > 1:
            root_element = self.create_union(primitives)
        elif len(primitives) == 1:
            root_element = primitives[0]

        result = []
        if root_element:
            if isinstance(root_element, BaseMultipartGeometry):
                for geom in root_element.geoms:
                    print(type(geom))
                    if isinstance(geom, Polygon):
                        result.append(QPolygonF(map(lambda c: QPointF(c[0], c[1]), list(geom.exterior.coords))))
                    else:
                        result.append(QPolygonF(map(lambda c: QPointF(c[0], c[1]), list(geom.coords))))
            else:
                result = [QPolygonF(map(lambda c: QPointF(c[0], c[1]), list(root_element.exterior.coords)))]

        return result
