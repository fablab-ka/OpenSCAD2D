from __future__ import print_function
import pprint
import math
import re
from pyparsing import lineno, col, line, Suppress, Keyword, oneOf, Literal, infixNotation, opAssoc, Word, alphas, \
    alphanums, nums, CaselessLiteral, Combine, Optional, Forward, ZeroOrMore, delimitedList, FollowedBy, \
    OneOrMore, restOfLine, cStyleComment, ParseException
from src.log_exceptions import *

if sys.version > '3':
    long = int

DEBUG = True

# #########################################################################################
##########################################################################################


class KINDS(object):
    NO_KIND = "NO_KIND"
    GLOBAL_VAR = "GLOBAL_VAR"
    MODULE = "MODULE"
    PARAMETER = "PARAMETER"

class StatementType(object):
    Primitive = "primitive"
    Modifier = "modifier"

class SharedData(object):
    def __init__(self):
        # index of the currently parsed function
        self.function_index = 0
        # name of the currently parsed function
        self.function_name = 0
        # number of parameters of the currently parsed function
        self.function_params = 0
        # number of local variables of the currently parsed function
        self.function_vars = 0


##########################################################################################
##########################################################################################


class ExceptionSharedData(object):
    """Class for exception handling data"""

    def __init__(self):
        # position in currently parsed text
        self.location = 0
        # currently parsed text
        self.text = ""

    def setpos(self, location, text):
        """Helper function for setting currently parsed text and position"""
        self.location = location
        self.text = text


exshared = ExceptionSharedData()


class SemanticException(Exception):
    """Exception for semantic errors found during parsing, similar to ParseException.
       Introduced because ParseException is used internally in pyparsing and custom
       messages got lost and replaced by pyparsing's generic errors.
    """

    def __init__(self, message, print_location=True):
        super(SemanticException, self).__init__()
        self._message = message
        self.location = exshared.location
        self.print_location = print_location
        if exshared.location is not None:
            self.line = lineno(exshared.location, exshared.text)
            self.col = col(exshared.location, exshared.text)
            self.text = line(exshared.location, exshared.text)
        else:
            self.line = self.col = self.text = None

    def _get_message(self):
        return self._message

    def _set_message(self, message):
        self._message = message

    message = property(_get_message, _set_message)

    def __str__(self):
        """String representation of the semantic error"""
        msg = "Error"
        if self.print_location and self.line is not None:
            msg += " at line %d, col %d" % (self.line, self.col)
        msg += ": %s" % self.message
        if self.print_location and self.line is not None:
            msg += "\n%s" % self.text
        return msg


##########################################################################################
##########################################################################################


class SymbolTableEntry(object):
    """Class which represents one symbol table entry."""

    def __init__(self, name="", kind=None, parent=None, value=None):
        """Initialization of symbol table entry.
           name - symbol name
           kind - symbol kind
        """
        self.name = name
        self.kind = kind
        self.parent = parent
        self.value = value
        self.parameters = []


class SymbolTable(object):
    def __init__(self):
        """Initialization of the symbol table"""
        self.table = []

    def error(self, text=""):
        """Symbol table error exception. It should happen only if index is out of range while accessing symbol table.
           This exception is not handled by the compiler, so as to allow traceback printing
        """
        if text == "":
            raise Exception("Symbol table index out of range")
        else:
            raise Exception("Symbol table error: %s" % text)

    def display(self):
        """Displays the symbol table content"""
        # Finding the maximum length for each column

        if len(self.table) <= 0:
            print("\n === NO DATA IN SYMBOL TABLE === \n")
            return

        sym_name = "Symbol name"
        sym_len = 0
        if len(self.table) > 0:
            sym_len = max(max(len(i.name) for i in self.table), len(sym_name))

        kind_name = "Kind"
        kind_len = 0
        if len(self.table) > 0:
            kind_len = max(max(len(i.kind) for i in self.table), len(kind_name))

        value_name = "Value"
        val_len = 0
        if len(self.table) > 0:
            val_len = max(max(len(str(i.value)) for i in self.table), len(value_name))

        param_name = "Parameters"
        param_len = 0
        if len(self.table) > 0:
            param_len = max(max(len(", ".join(i.parameters))+2 for i in self.table), len(param_name))

        seperator = "|--------------" + ("-" * (sym_len + kind_len + val_len + param_len) ) + "--|"

        # print table header
        print("\n" + seperator)
        print("|{0:3s} | {1:^{2}s} | {3:^{4}s} | {5:^{6}s} | {7:^{8}s} |".format(" No", sym_name, sym_len, kind_name, kind_len, value_name, val_len, param_name, param_len))
        print(seperator)
        # print symbol table
        for i, sym in enumerate(self.table):
            print("|{0:3d} | {1:^{2}s} | {3:^{4}s} | {5:^{6}s} | ({7:^{8}s}) |".format(i, sym.name, sym_len, sym.kind, kind_len, str(sym.value), val_len, ", ".join(sym.parameters), param_len-2))
        print(seperator + "\n")

    def insert_global_var(self, name, value):
        return self.insert_id(name, KINDS.GLOBAL_VAR, None, value)

    def insert_parameter(self, name, module):
        index = self.insert_id(name, KINDS.PARAMETER, module, None)
        for entry in self.table:
            if entry.name == module and entry.kind == KINDS.MODULE:
                entry.parameters.append(name)
                break
        return index

    def insert_module(self, name):
        index = self.insert_id(name, KINDS.MODULE, None)
        return index

    def insert_id(self, name, kind, parent, value):
        if not self.contains(name, KINDS.GLOBAL_VAR, parent):
            index = self.insert(name, kind, parent, value)
            return index
        else:
            raise SemanticException("Redefinition of '%s'" % name)

    def contains(self, name, kind, parent):
        result = False

        for entry in self.table:
            if entry.name == name and entry.kind == kind and entry.parent == parent:
                result = True
                break

        return result

    def get_value(self, name, kind, parent):
        result = False

        for entry in self.table:
            if entry.name == name and entry.kind == kind and entry.parent == parent:
                result = entry.value
                break

        return result

    def insert(self, name, kind, parent, value):
        self.table.append(SymbolTableEntry(name, kind, parent, value))
        return len(self.table)


##########################################################################################
##########################################################################################

class Vector(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "{VECTOR: " + repr(self.x) + " : " + repr(self.y) + "}"

class Scope(object):
    def __init__(self, name, arguments, children, modifiers):
        self.name = name
        self.arguments = arguments
        self.children = children
        self.modifiers = modifiers

    def __repr__(self):
        return "{SCOPE: " + self.name + " - " + repr(self.arguments) + " - " + repr(self.children) + " - " + repr(self.modifiers) + "}"

class Statement(object):
    def __init__(self, statement_type, name, arguments, modifiers=None):
        self.type = statement_type
        self.name = name
        self.arguments = arguments
        self.modifiers = modifiers

    def __repr__(self):
        return "{STATEMENT: " + self.type + " - " + self.name + " - " + repr(self.arguments) + " - " + repr(self.modifiers) + "}"

class Constant(object):
    def __init__(self, data):
        self.value = data[0]
        #self.type = data[1]

    def __repr__(self):
        return "{CONSTANT: " + str(self.value) + "}"# (" + self.type + ")}"

class Variable(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return "{VARIABLE: " + str(self.identifier) + "}"

class Assignment(object):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def __repr__(self):
        return "{ASSIGNMENT: " + repr(self.identifier) + " = " + repr(self.value) + "}"

class BoolOperand(object):
    def __init__(self,t):
        self.label = t[0]
        self.value = True if t[0].lower().strip() == "true" else False
    def __bool__(self):
        return self.value
    def __str__(self):
        return self.label
    __repr__ = __str__
    __nonzero__ = __bool__

class BoolBinOp(object):
    def __init__(self,t):
        self.args = t[0][0::2]
    def __str__(self):
        sep = " %s " % self.reprsymbol
        return "(" + sep.join(map(str,self.args)) + ")"
    def __bool__(self):
        return self.evalop(bool(a) for a in self.args)
    __nonzero__ = __bool__
    __repr__ = __str__

class BoolAnd(BoolBinOp):
    reprsymbol = '&'
    evalop = all

class BoolOr(BoolBinOp):
    reprsymbol = '|'
    evalop = any

class BoolNot(object):
    def __init__(self,t):
        self.arg = t[0][1]
    def __bool__(self):
        v = bool(self.arg)
        return not v
    def __str__(self):
        return "~" + str(self.arg)
    __repr__ = __str__
    __nonzero__ = __bool__

class UnresolvedCalculation(object):
    def __init__(self, stack):
        self.stack = stack

    def __repr__(self):
        return "{UNRESOLVED_CALCULATION: " + repr(self.stack) + "}"

##########################################################################################
##########################################################################################


class FcadParser(object):
    def __init__(self, filename):
        self.filename = filename
        self.program = None

        self.symtab = SymbolTable()

        self.init_grammar()

        self.operators = {
            "+" : ( lambda a,b: a + b ),
            "-" : ( lambda a,b: a - b ),
            "*" : ( lambda a,b: a * b ),
            "/" : ( lambda a,b: a / b ),
            "^" : ( lambda a,b: a ** b )
        }

        self.exprStack = []

    def evaluateStack(self, s):
        op = s.pop()
        if isinstance(op, UnresolvedCalculation):
            return op
        if isinstance(op, long) or isinstance(op, float) or isinstance(op, int):
            return op
        if op in "+-*/^":
            op2 = self.evaluateStack( s )
            op1 = self.evaluateStack( s )
            if isinstance(op1, Variable) or isinstance(op2, Variable) or \
               isinstance(op1, UnresolvedCalculation) or isinstance(op2, UnresolvedCalculation):
                return UnresolvedCalculation([op1, op2, op])
            else:
                return self.operators[op]( op1, op2 )
        elif op == "PI":
            return math.pi
        elif op == "E":
            return math.e
        elif re.search('^[a-zA-Z][a-zA-Z0-9_]*$',op):
            if self.symtab.contains(op, KINDS.GLOBAL_VAR, None):
                return self.symtab.get_value(op, KINDS.GLOBAL_VAR, None)
            else:
                return Variable(op)
        elif re.search('^[-+]?[0-9]+$',op):
            return long( op )
        else:
            return float( op )

    def pushFirst( self, str, loc, toks ):
        self.exprStack.append( toks[0] )

    def calculate(self, text, loc, toks):
        return self.evaluateStack(self.exprStack)

    # noinspection PyPep8Naming,PyShadowingBuiltins
    def init_grammar(self):
        LPAR, RPAR, LBRACK, RBRACK, LBRACE, RBRACE, SEMI, COMMA, EQUAL, COLON = map(Suppress, "()[]{};,=:")

        USE = Keyword("use")
        MODULE = Keyword("module")
        IF = Keyword("if")
        FOR = Keyword("for")
        ELSE = Keyword("else")
        TRUE = Keyword("true")
        FALSE = Keyword("false")
        UNDEF = Keyword("undef")
        mul_operator = oneOf("* /")
        add_operator = oneOf("+ -")
        exp_operator = Literal( "^" )

        boolOperand = ( TRUE | FALSE )
        boolOperand.setParseAction(BoolOperand)

        boolExpr = infixNotation( boolOperand, [
            ("not", 1, opAssoc.RIGHT, BoolNot),
            ("and", 2, opAssoc.LEFT,  BoolAnd),
            ("or",  2, opAssoc.LEFT,  BoolOr),
        ])

        identifier = Word("$" + alphas + "_", alphanums + "_")
        plusorminus = Literal('+') | Literal('-')
        numberal = Word(nums)
        e = CaselessLiteral('E')
        integer = Combine( Optional(plusorminus) + numberal )
        floatnumber = Combine( integer +
                       Optional( Literal('.') + Optional(numberal) ) +
                       Optional( e + integer )
                     )
        number = ( integer | floatnumber )

        calculation = Forward()
        atom = ( ( e | floatnumber | integer | identifier ).setParseAction( self.pushFirst ) |
                 ( LPAR + calculation.suppress() + RPAR )
               )

        factor = Forward()
        factor << atom + ZeroOrMore( ( exp_operator + factor ).setParseAction( self.pushFirst ) )

        term = factor + ZeroOrMore( ( mul_operator + factor ).setParseAction( self.pushFirst ) )
        calculation << term + ZeroOrMore( ( add_operator + term ).setParseAction( self.pushFirst ) )
        calculation.setParseAction(self.calculate)


        constant = number.setParseAction(self.constant_action)
        modifier_name = ( Keyword("translate") | Keyword("rotate") | Keyword("scale") | Keyword("simplify") )

        use = (USE + identifier("name") + SEMI).setParseAction(self.use_action)

        expression = Forward()

        arguments = delimitedList(expression("exp").setParseAction(self.argument_action))
        module_call = ((identifier("name") + FollowedBy("(")).setParseAction(self.module_call_prepare_action) +
                       LPAR + Optional(arguments)("args") + RPAR)
        module_call_statement = (module_call + SEMI).setParseAction(self.module_call_action)

        primitive_argument_assignment_value = (calculation | boolExpr)

        primitive_argument_assignment = (identifier("variable") + EQUAL + primitive_argument_assignment_value).setParseAction(self.primitive_argument_assignment_action)
        primitive_argument = (primitive_argument_assignment | expression("exp"))
        primitive_argument_list = delimitedList(primitive_argument.setParseAction(self.argument_action))

        modifier = ( (modifier_name + FollowedBy("(")).setParseAction(self.primitive_modifier_prepare_action) +
                              LPAR + Optional(primitive_argument_list)("args") + RPAR).setParseAction(self.primitive_modifier_action)

        primitive_call_statement = ( ZeroOrMore(modifier)("modifiers") + (identifier("name") + FollowedBy("(")).setParseAction(self.primitive_call_prepare_action) +
                                    LPAR + Optional(primitive_argument_list)("args") + RPAR + SEMI).setParseAction(self.primitive_call_action)

        expression << (boolExpr | calculation).setParseAction(self.debug_action)#.setParseAction(lambda x: x[0])

        statement = Forward()

        assign_statement = (identifier("variable") + EQUAL + expression("expression") + SEMI).setParseAction(self.assign_action)

        modifier_scope = ( (ZeroOrMore(modifier)("modifiers") + identifier("name") + LPAR + Optional(primitive_argument_list)("args") + RPAR + FollowedBy("{")).setParseAction(self.modifier_scope_prepare_action) +
                            LBRACE + ZeroOrMore(statement) + RBRACE ).setParseAction(self.modifier_scope_action)

        vector = (LBRACK + calculation + COLON + calculation + RBRACK).setParseAction(self.vector_action)

        for_loop_scope = ( ZeroOrMore(modifier)("modifiers") + ( FOR + LPAR + identifier("index") + EQUAL + vector("loop_range") + RPAR + FollowedBy("{") ).setParseAction(self.begin_for_loop_scope) +
                         LBRACE + ZeroOrMore(statement)("body") + RBRACE ).setParseAction(self.for_loop_scope_action)

        statement << ( for_loop_scope | primitive_call_statement | module_call_statement | Suppress(assign_statement) | modifier_scope )

        body = OneOrMore(statement)

        self.program = (ZeroOrMore(use) + body).setParseAction(self.program_end_action)

    @log_exceptions(log_if=DEBUG)
    def debug_action(self, text, loc, stuff):
        return stuff

    @log_exceptions(log_if=DEBUG)
    def vector_action(self, text, loc, tokens):
        if DEBUG:
            print("vector_action:", tokens)
            self.symtab.display()
        return Vector(tokens[0], tokens[1])

    @log_exceptions(log_if=DEBUG)
    def begin_for_loop_scope(self, text, loc, tokens):
        if DEBUG:
            print("begin_for_loop_scope:", tokens)
            self.symtab.display()

        return [tokens.index, tokens.loop_range]

    @log_exceptions(log_if=DEBUG)
    def for_loop_scope_action(self, text, loc, tokens):

        if DEBUG:
            print("for_loop_scope_action:", tokens)
            self.symtab.display()

        result = []
        variable = tokens[0]
        loop_range = tokens[1]
        for i in range(loop_range.x, loop_range.y):
            assignment = Assignment(variable, i)
            assignment_scope = Scope("assign", [assignment], tokens.body, [])
            result.append(assignment_scope)

        return result

    @log_exceptions(log_if=DEBUG)
    def lookup_id_action(self, text="", loc=-1, var=None):
        """Code executed after recognising an identificator in expression"""
        
        varname = text if not var else var.name
        exshared.setpos(loc, text)
        if DEBUG:
            print("EXP_VAR:", var)
            self.symtab.display()

        if not self.symtab.contains(varname, KINDS.GLOBAL_VAR, None):
            raise SemanticException("'%s' undefined" % varname)
        return [Variable(varname)]

    @log_exceptions(log_if=DEBUG)
    def constant_action(self, text, loc, const):
        """Code executed after recognising a constant"""
        exshared.setpos(loc, text)
        if DEBUG:
            print("CONST:", const)
            self.symtab.display()
        return Constant(const)

    @log_exceptions(log_if=DEBUG)
    def assign_action(self, text, loc, assign):
        if DEBUG:
            print("ASSIGN:", assign)
            self.symtab.display()

        self.symtab.insert_global_var(assign.variable, assign.expression)
        return None

    @log_exceptions(log_if=DEBUG)
    def use_action(self, text, loc, use):
        if DEBUG:
            print("use_action")
        return "use_token"

    @log_exceptions(log_if=DEBUG)
    def argument_action(self, text, loc, argument):
        if DEBUG:
            print("argument_action",loc, argument)

    @log_exceptions(log_if=DEBUG)
    def module_call_prepare_action(self, text, loc, argument):
        if DEBUG:
            print("module_call_prepare_action")

    @log_exceptions(log_if=DEBUG)
    def module_call_action(self, text, loc, call_name):
        if DEBUG:
            print("module_call_action")
        return call_name[0]

    @log_exceptions(log_if=DEBUG)
    def primitive_call_prepare_action(self, text, loc, call_name):
        if DEBUG:
            print("primitive_call_prepare_action",loc, call_name)
        return call_name[0]

    @log_exceptions(log_if=DEBUG)
    def primitive_argument_assignment_action(self, text, loc, assignment):
        if DEBUG:
            print("primitive_argument_assignment_action", assignment)
        return Assignment(assignment[0], assignment[1])

    @log_exceptions(log_if=DEBUG)
    def primitive_call_action(self, text, loc, call):
        if DEBUG:
            print("primitive_call_action",loc, call)
        modifiers = list(filter(lambda c: isinstance(c, Statement) and c.type == StatementType.Modifier, call))
        name = call[len(modifiers)]
        arguments = call[len(modifiers)+1:]
        return Statement(StatementType.Primitive, name, arguments, modifiers)

    @log_exceptions(log_if=DEBUG)
    def primitive_modifier_prepare_action(self, text, loc, modifier):
        if DEBUG:
            print("primitive_modifier_prepare_action",loc, modifier)
        return modifier[0]

    @log_exceptions(log_if=DEBUG)
    def primitive_modifier_action(self, text, loc, modifier):
        if DEBUG:
            print("primitive_modifier_action",loc, modifier)
        arguments = modifier[1:]
        return Statement(StatementType.Modifier, modifier[0], arguments)

    @log_exceptions(log_if=DEBUG)
    def modifier_scope_prepare_action(self, text, loc, scope):
        if DEBUG:
            print("modifier_scope_prepare_action",loc, scope)

        return Scope(scope.name, scope.args, [], scope.modifiers)

    @log_exceptions(log_if=DEBUG)
    def modifier_scope_action(self, text, loc, scope):
        if DEBUG:
            print("modifier_scope_action",loc, scope)

        result = scope[0]
        result.children = scope[1:]
        return result

    @log_exceptions(log_if=DEBUG)
    def program_end_action(self, text, loc, scope):
        if DEBUG:
            print("program_end_action")

    def parse(self):
        result, error = None, None
        #f = open(self.filename, 'r')
        #text = f.read()
        #f.close()

        #print(text)

        try:
            singleLineComment = "//" + restOfLine
            self.program.ignore(singleLineComment)
            self.program.ignore(cStyleComment)
            result = self.program.parseFile(self.filename, parseAll=True)
            pprint.pprint(result)
        except SemanticException as ex:
            error = "failed to parse input. " + repr(ex)
        except ParseException as ex:
            error = "failed to parse input. " + repr(ex)

        return result, error
