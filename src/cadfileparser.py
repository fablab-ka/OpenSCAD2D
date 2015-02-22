import pprint
from pyparsing import *

# defines debug level
# 0 - no debug
# 1 - print parsing results
# 2 - print parsing results and symbol table
# 3 - print parsing results only, without executing parse actions (grammar-only testing)
DEBUG = 2

# #########################################################################################
##########################################################################################


class KINDS:
    NO_KIND = "NO_KIND"
    GLOBAL_VAR = "GLOBAL_VAR"
    MODULE = "MODULE"
    PARAMETER = "PARAMETER"

class StatementType:
    Primitive = "primitive"
    Modifier = "modifier"
    NOP = "NOP"

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
        if exshared.location != None:
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
        if self.print_location and (self.line != None):
            msg += " at line %d, col %d" % (self.line, self.col)
        msg += ": %s" % self.message
        if self.print_location and (self.line != None):
            msg += "\n%s" % self.text
        return msg


##########################################################################################
##########################################################################################


class SymbolTableEntry(object):
    """Class which represents one symbol table entry."""

    def __init__(self, name="", kind=None, parent=None):
        """Initialization of symbol table entry.
           name - symbol name
           kind - symbol kind
        """
        self.name = name
        self.kind = kind
        self.parent = parent
        self.parameters = []


class SymbolTable:
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
        sym_name = "Symbol name"
        sym_len = 0
        if len(self.table) > 0:
            sym_len = max(max(len(i.name) for i in self.table), len(sym_name))
        kind_name = "Kind"
        kind_len = 0
        if len(self.table) > 0:
            kind_len = max(max(len(i.kind) for i in self.table), len(kind_name))
        # print table header
        print "{0:3s} | {1:^{2}s} | {3:^{4}s} | {5:s}".format(" No", sym_name, sym_len, kind_name, kind_len,
                                                              "Parameters")
        print "-----------------------------" + "-" * (sym_len + kind_len)
        # print symbol table
        for i, sym in enumerate(self.table):
            parameters = ""
            for p in sym.parameters:
                if parameters == "":
                    parameters = p
                else:
                    parameters += ", " + p
            print "{0:3d} | {1:^{2}s} | {3:^{4}s} | ({5})".format(i, sym.name, sym_len, sym.kind, kind_len, parameters)

    def insert_global_var(self, name):
        return self.insert_id(name, KINDS.GLOBAL_VAR)

    def insert_parameter(self, name, module):
        index = self.insert_id(name, KINDS.PARAMETER, module)
        for entry in self.table:
            if entry.name == module and entry.kind == KINDS.MODULE:
                entry.parameters.append(name)
                break
        return index

    def insert_module(self, name):
        index = self.insert_id(name, KINDS.MODULE)
        return index

    def insert_id(self, name, kind, parent=None):
        """Inserts a new identifier at the end of the symbol table, if possible.
           Returns symbol index, or raises an exception if the symbol already exists
           name   - symbol name
           kind   - symbol kind
        """
        if not self.contains(name, KINDS.GLOBAL_VAR, parent):
            index = self.insert(name, kind, parent)
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

    def insert(self, name, kind, parent):
        self.table.append(SymbolTableEntry(name, kind, parent))
        return len(self.table)


##########################################################################################
##########################################################################################

class Statement:
    def __init__(self, type, name, arguments, modifiers=None):
        self.type = type
        self.name = name
        self.arguments = arguments
        self.modifiers = modifiers

    def __repr__(self):
        return "[STATEMENT: " + self.type + " - " + self.name + " - " + repr(self.arguments) + " - " + repr(self.modifiers) + "]"

class Constant:
    def __init__(self, data):
        self.value = data[0]
        self.type = data[1]

    def __repr__(self):
        return "[CONSTANT: " + self.value + " (" + self.type + ")]"

class Variable:
    def __init__(self, identifier):
        self.identifier = identifier

class Assignment:
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    #def __repr__(self):
     #   return "[ASSIGNMENT: " + self.identifier + " = " + self.value + "]"

##########################################################################################
##########################################################################################


class FcadParser:
    def __init__(self, filename):
        self.filename = filename
        self.program = None

        self.symtab = SymbolTable()

        self.init_grammar()

    # noinspection PyPep8Naming,PyShadowingBuiltins
    def init_grammar(self):
        LPAR, RPAR, LBRACK, RBRACK, LBRACE, RBRACE, SEMI, COMMA, EQUAL = map(Suppress, "()[]{};,=")

        USE = Keyword("use")
        MODULE = Keyword("module")
        FUNCTION = Keyword("function")
        IF = Keyword("if")
        ELSE = Keyword("else")
        TRUE = Keyword("true")
        FALSE = Keyword("false")
        UNDEF = Keyword("undef")
        mul_operator = oneOf("* /")
        add_operator = oneOf("+ -")

        identifier = Word(alphas + "_", alphanums + "_")
        integer = Word(nums).setParseAction(lambda x: [x[0], "INT"])
        floatnumber = Regex(r"[-+]?[0-9]*\.?[0-9]+")
        number = integer | floatnumber
        constant = number.setParseAction(self.constant_action)
        modifier_name = ( Keyword("translate") |Keyword("rotate") | Keyword("scale") )

        use = (USE + identifier("name") + SEMI).setParseAction(self.use_action)

        expression = Forward()
        mul_expression = Forward()
        num_expression = Forward()

        arguments = delimitedList(expression("exp").setParseAction(self.argument_action))
        module_call = ((identifier("name") + FollowedBy("(")).setParseAction(self.module_call_prepare_action) +
                       LPAR + Optional(arguments)("args") + RPAR)
        module_call_statement = (module_call + SEMI).setParseAction(self.module_call_action)

        primitive_argument_assignment_value = (constant |
                                               identifier("name").setParseAction(self.lookup_id_action) |
                                               Group(Suppress("(") + num_expression + Suppress(")")) )

        primitive_argument_assignment = (identifier("variable") + EQUAL + primitive_argument_assignment_value).setParseAction(self.primitive_argument_assignment_action)
        primitive_argument = (primitive_argument_assignment | expression("exp"))
        primitive_argument_list = delimitedList(primitive_argument.setParseAction(self.argument_action))

        primitive_modifier = ( (modifier_name + FollowedBy("(")).setParseAction(self.primitive_modifier_prepare_action) +
                              LPAR + Optional(primitive_argument_list)("args") + RPAR).setParseAction(self.primitive_modifier_action)

        primitive_call_statement = ( ZeroOrMore(primitive_modifier) + (identifier("name") + FollowedBy("(")).setParseAction(self.primitive_call_prepare_action) +
                                    LPAR + Optional(primitive_argument_list)("args") + RPAR + SEMI).setParseAction(self.primitive_call_action)

        expression << (constant |
                       identifier("name").setParseAction(self.lookup_id_action) |
                       Group(Suppress("(") + num_expression + Suppress(")")) |
                       Group("+" + expression) |
                       Group("-" + expression)).setParseAction(lambda x: x[0])
        mul_expression << (expression + ZeroOrMore(mul_operator + expression))
        num_expression << (mul_expression + ZeroOrMore(add_operator + mul_expression))

        statement = Forward()

        assign_statement = (identifier("variable") + EQUAL + num_expression("expression") +
                            SEMI).setParseAction(self.assign_action)

        statement << (primitive_call_statement | module_call_statement | assign_statement)

        body = OneOrMore(statement)

        self.program = (ZeroOrMore(use) + body).setParseAction(self.program_end_action)

    def lookup_id_action(self, text="", loc=-1, var=None):
        varname = text if not var else var.name
        """Code executed after recognising an identificator in expression"""
        exshared.setpos(loc, text)
        if DEBUG > 0:
            print "EXP_VAR:", var
            if DEBUG == 2: self.symtab.display()
            if DEBUG > 2: return
        if not self.symtab.contains(varname, KINDS.GLOBAL_VAR, None):
            raise SemanticException("'%s' undefined" % varname)
        return [Variable(varname)]

    def constant_action(self, text, loc, const):
        """Code executed after recognising a constant"""
        exshared.setpos(loc, text)
        if DEBUG > 0:
            print "CONST:", const
            if DEBUG == 2: self.symtab.display()
            if DEBUG > 2: return
        return Constant(const)

    def assign_action(self, text, loc, assign):
        if DEBUG > 0:
            print "ASSIGN:", assign
            if DEBUG == 2: self.symtab.display()
            if DEBUG > 2: return

        index = self.symtab.insert_global_var(assign.variable)
        return StatementType.NOP

    def use_action(self, text, loc, use):
        if DEBUG > 0:
            print "use_action"
        return "use_token"

    def argument_action(self, text, loc, argument):
        if DEBUG > 0:
            print "argument_action",loc, argument

    def module_call_prepare_action(self, text, loc, argument):
        if DEBUG > 0:
            print "module_call_prepare_action"

    def module_call_action(self, text, loc, call_name):
        if DEBUG > 0:
            print "module_call_action"
        return call_name[0]

    def primitive_call_prepare_action(self, text, loc, call_name):
        if DEBUG > 0:
            print "primitive_call_prepare_action",loc, call_name
        return call_name[0]

    def primitive_argument_assignment_action(self, text, loc, assignment):
        if DEBUG > 0:
            print "primitive_argument_assignment_action", assignment
        return Assignment(assignment[0], assignment[1])

    def primitive_call_action(self, text, loc, call):
        if DEBUG > 0:
            print "primitive_call_action",loc, call
        modifiers = filter(lambda c: isinstance(c, Statement) and c.type == StatementType.Modifier, call)
        name = call[len(modifiers)]
        arguments = call[len(modifiers)+1:]
        return Statement(StatementType.Primitive, name, arguments, modifiers)

    def primitive_modifier_prepare_action(self, text, loc, modifier):
        if DEBUG > 0:
            print "primitive_modifier_prepare_action",loc, modifier
        return modifier[0]

    def primitive_modifier_action(self, text, loc, modifier):
        if DEBUG > 0:
            print "primitive_modifier_action",loc, modifier
        arguments = modifier[1:]
        return Statement(StatementType.Modifier, modifier[0], arguments)

    def program_end_action(self):
        if DEBUG > 0:
            print "program_end_action"

    def parse(self):
        result, error = None, None
        #f = open(self.filename, 'r')
        #text = f.read()
        #f.close()

        #print text

        try:
            singleLineComment = "//" + restOfLine
            self.program.ignore(singleLineComment)
            self.program.ignore(cStyleComment)
            result = self.program.parseFile(self.filename, parseAll=True)
            pprint.pprint(result)
        except SemanticException, ex:
            error = "failed to parse input. " + repr(ex)
        except ParseException as ex:
            error = "failed to parse input. " + repr(ex)

        return result, error
