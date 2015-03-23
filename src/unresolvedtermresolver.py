from src import cadfileparser

__author__ = 'sven'


class UnresolvedTermResolver(object):
    def __init__(self):
        self.assignment_stack = []
        self.parser = cadfileparser.FcadParser(None)

    def lookup_variable_value(self, variable):
        value = None

        for assignment in self.assignment_stack:
            if assignment.identifier == variable.identifier:
                value = assignment.value
                break

        if value is not None:
            variable.value = value
        return value

    def calculate(self, calculation):
        calculation_stack = self.resolve_calculation(calculation)

        result = self.parser.evaluateStack(calculation_stack)

        if isinstance(result, cadfileparser.UnresolvedCalculation):
            raise cadfileparser.SemanticException("Calculation stack '" + repr(calculation) + "' could not be resolved.")

        return result

    def resolve_calculation(self, calculation):
        result = []
        for i in range(len(calculation.stack)):
            term = self.resolve_calculation_term(calculation.stack[i])
            result.append(term)

        return result

    def resolve_calculation_term(self, calculation):
        if isinstance(calculation, cadfileparser.Variable):
            value = self.lookup_variable_value(calculation)

            if value is None:
                raise cadfileparser.SemanticException("variable '" + repr(calculation) + "' could not be resolved. Expected numerical term.")

            calculation = value
        elif isinstance(calculation, list):
            calculation = self.resolve_calculation(calculation)
        elif isinstance(calculation, cadfileparser.UnresolvedCalculation):
            calculation = self.calculate(calculation)

        return calculation