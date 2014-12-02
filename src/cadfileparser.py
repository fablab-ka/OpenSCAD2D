import pprint
from pyparsing import *


class FcadParser:
    def __init__(self, filename):
        self.filename = filename
        self.program = None
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

        identifier = Word(alphas + "_", alphanums + "_")
        integer = Regex(r"[+-]?\d+")
        floatnumber = Regex(r"[-+]?[0-9]*\.?[0-9]+")
        number = integer | floatnumber

        input = Forward()
        statement = Forward()

        input << empty | USE + input | statement + input

        body = Forward()
        body << empty | statement + body

        module_instantiation = Forward()
        expression = Forward()
        parameters = Forward()
        optional_commas = Forward()
        module_instantiation_list = Forward()
        single_module_instantiation = Forward()
        arguments = Forward()
        vector_expr = Forward()

        #Null operation statement is superfluous
        statement << SEMI | \
            LBRACE + body + RBRACE | \
            module_instantiation | \
            identifier + EQUAL + expression + SEMI | \
            MODULE + identifier + LPAR + parameters + optional_commas + RPAR + statement | \
            FUNCTION + identifier + LPAR + parameters + optional_commas + RPAR + EQUAL + expression + SEMI
        #Optional commas in the above two seem strange to me. We can have for e.g. module foo(a,,,,,,b){} how on earth can this be useful?
        #I agree that is makes sence for a module instantiation because we might want to pass undef, but for declarations its just a way
        #of ensuring we don't have access to unnamed module parameters, so why have them at all?
        
        children_instantiation = \
            module_instantiation | \
            LBRACE + module_instantiation_list + RBRACE
        
        if_statement = IF + LPAR + expression + RPAR + children_instantiation
        # why can't we just have statements in our if  why is the following invalid!? if(true) { a=1; cube([10,a,10]); }
        
        ifelse_statement = \
            if_statement | \
            if_statement + ELSE + children_instantiation

        module_instantiation << \
            single_module_instantiation + SEMI | \
            single_module_instantiation + children_instantiation | \
            ifelse_statement

        module_instantiation_list <<  empty | module_instantiation_list + module_instantiation

        # this is interesting, you can have a label before a module instantiation e.g. foo: cube([10,10,10]); although what this is for I have no idea.
        single_module_instantiation << \
            identifier + LPAR + arguments + RPAR | \
            identifier + ':' + single_module_instantiation | \
            '!' + single_module_instantiation | \
            '#' + single_module_instantiation | \
            '%' + single_module_instantiation | \
            '*' + single_module_instantiation
        
        expression << \
            TRUE | \
            FALSE | \
            UNDEF | \
            identifier | \
            expression + '.' + identifier | \
            dblQuotedString | \
            number | \
            LBRACK + expression + ':' <expression> RBRACK | \
            LBRACK + expression + ':' <expression> ':' <expression> RBRACK | \
            LBRACK + optional_commas + RBRACK | \
            LBRACK + vector_expr + optional_commas + RBRACK | \
            expression + '*' + expression | \
            expression + '/' + expression | \
            expression + '%' + expression | \
            expression + '+' + expression | \
            expression + '-' + expression | \
            expression + '<' + expression | \
            expression + "<=" + expression | \
            expression + "==" + expression | \
            expression + "!=" + expression | \
            expression + ">=" + expression | \
            expression + '>' + expression | \
            expression + "&&" + expression | \
            expression + "||" + expression | \
            '+' + expression | \
            '-' + expression | \
            '!' + expression | \
            LPAR + expression + RPAR | \
            expression + '?' + expression + ':' + expression | \
            expression + '[' + expression + RBRACK | \
            identifier + LPAR + arguments + RPAR
        
        optional_commas << \
            empty | \
            ',' + optional_commas
        
        vector_expr << \
            expression | \
            vector_expr + ',' + optional_commas + expression

        parameter = \
            identifier | \
            identifier + EQUAL + expression
        
        parameters << \
            empty | \
            parameter | \
            parameters + ',' + optional_commas + parameter

        argument = \
            expression | \
            identifier + EQUAL + expression

        arguments << \
            empty | \
            argument | \
            arguments + ',' + optional_commas + argument

        self.program = input + body

    # noinspection PyPep8Naming,PyUnusedLocal
    def init_program(self):
        LPAR, RPAR, LBRACK, RBRACK, LBRACE, RBRACE, SEMI, COMMA = map(Suppress, "()[]{};,")
        WHILE = Keyword("while")
        DO = Keyword("do")
        IF = Keyword("if")
        ELSE = Keyword("else")
        RETURN = Keyword("return")
        MODULE = Keyword("module")

        UNION = Keyword("union")
        DIFFERENCE = Keyword("difference")
        INTERSECTION = Keyword("intersection")
        TRANSLATE = Keyword("translate")
        ROTATE = Keyword("rotate")
        HULL = Keyword("hull")

        NAME = Word(alphas + "_", alphanums + "_")
        integer = Regex(r"[+-]?\d+")
        floatnumber = Regex(r"[-+]?[0-9]*\.?[0-9]+")
        char = Regex(r"'.'")
        string_ = dblQuotedString

        expr = Forward()
        operand = NAME | integer | char | string_
        expr << (operatorPrecedence(operand, [
            (oneOf('! -'), 1, opAssoc.RIGHT),
            (oneOf('++ --'), 1, opAssoc.RIGHT),
            (oneOf('++ --'), 1, opAssoc.LEFT),
            (oneOf('* / %'), 2, opAssoc.LEFT),
            (oneOf('+ -'), 2, opAssoc.LEFT),
            (oneOf('< == > <= >= !='), 2, opAssoc.LEFT),
            (Regex(r'=[^=]'), 2, opAssoc.LEFT),
        ]) + Optional(LBRACK + expr + RBRACK | LPAR + Group(Optional(delimitedList(expr))) + RPAR)
        )

        vector = LBRACK + floatnumber + "," + floatnumber + RBRACK

        stmt = Forward()
        scope = Forward()

        ifstmt = IF - LPAR + expr + RPAR + stmt + Optional(ELSE + stmt)
        whilestmt = WHILE - LPAR + expr + RPAR + stmt
        dowhilestmt = DO - stmt + WHILE + LPAR + expr + RPAR + SEMI
        returnstmt = RETURN - expr + SEMI

        stmt << Group(ifstmt |
                      whilestmt |
                      dowhilestmt |
                      returnstmt |
                      expr + SEMI |
                      scope |
                      LBRACE + ZeroOrMore(stmt) + RBRACE |
                      SEMI)

        scopeparams = vector | NAME
        scopetype = UNION | DIFFERENCE | INTERSECTION | TRANSLATE | ROTATE | HULL
        scope << Group(scopetype + LPAR + Optional(scopeparams) + RPAR + stmt)

        vardecl = Group(NAME + Optional(LBRACK + integer + RBRACK)) + SEMI

        arg = NAME
        body = ZeroOrMore(vardecl) + ZeroOrMore(stmt)
        fundecl = Group(MODULE + NAME + LPAR + Optional(Group(delimitedList(arg))) + RPAR +
                        LBRACE + Group(body) + RBRACE)

        decl = fundecl | vardecl | scope

        program = ZeroOrMore(decl)

        program.ignore(cStyleComment)

        # set parser element names
        for vname in ("ifstmt whilestmt dowhilestmt returnstmt scope vector "
                      "NAME fundecl vardecl program arg body stmt".split()):
            v = vars()[vname]
            v.setName(vname)

        self.program = program

    def parse(self):
        f = open(self.filename, 'r')
        text = f.read()
        f.close()

        print text

        try:
            ast = self.program.parseString(text, parseAll=True)
            pprint.pprint(ast.asList())
        except ParseException as ex:
            print "failed to parse input.", ex
