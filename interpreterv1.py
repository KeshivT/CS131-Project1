from brewparse import parse_program
from intbase import InterpreterBase, ErrorType

class Interpreter(InterpreterBase):
    # Init
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor

    # Program Node
    def run(self, program):
        # Pretty much copied from provided pseudocode
        # Runs the main function
        ast = parse_program(program)         # parse program into AST
        self.variable_name_to_value = {}  # dict to hold variables
        main_func_node = self.get_main_func_node(ast)
        self.run_func(main_func_node)


    # Function Definition Node
    def get_main_func_node(self, ast):
        # Get main function
        if ast.elem_type != InterpreterBase.PROGRAM_NODE:
            return None
        
        functions = ast.get('functions')

        if functions is None:
            return None
        for func in functions:
            if func.elem_type == InterpreterBase.FUNC_NODE:
                func_name = func.get('name')
                if func_name == 'main':
                    return func
                else:
                    super().error(ErrorType.NAME_ERROR, "No main() function was found")
                    
        return None

    def run_func(self, func_node):
        # Also mostly copied from pseudocode, added check for no statements
        # Go through statements in the function and run them
        statements = func_node.get('statements')
        if statements is None:
            return
        for statement_node in statements:
            self.run_statement(statement_node)


    # Statement Nodes
    def run_statement(self, statement_node):
        # I dedicate this code to my best friend, Provided Pseudocode. It has never let me down.
        # Checks type of statement and runs it
        if statement_node.elem_type == InterpreterBase.VAR_DEF_NODE:
            self.do_definition(statement_node)
        elif statement_node.elem_type == InterpreterBase.ASSIGNMENT_NODE:
            self.do_assignment(statement_node)
        elif statement_node.elem_type == InterpreterBase.FCALL_NODE:
            self.do_func_call(statement_node)
        else:
            super().error(ErrorType.TYPE_ERROR, f"Unknown statement type: {statement_node.elem_type}")
        
    # Variable Definition Statement
    def do_definition(self, statement_node):
        var_name = statement_node.get('name')
        if var_name in self.variable_name_to_value:
            super().error(ErrorType.NAME_ERROR, f"Vairable {var_name} already defined")
        self.variable_name_to_value[var_name] = None
       
    # Assignemnt Statement
    def do_assignment(self, statement_node):
        # Credit to pseudocode!
        target_var_name = statement_node.get('name')
        if not target_var_name in self.variable_name_to_value:
            super().error(ErrorType.NAME_ERROR, f"Variable {target_var_name} not defined")
        source_node = statement_node.get('expression')
        resulting_value = self.evaluate_expression(source_node)
        self.variable_name_to_value[target_var_name] = resulting_value

    # Function Call Statment
    def do_func_call(self, statement_node):
        func_name = statement_node.get('name')
        args = statement_node.get('args')

        # Check type of function call and run
        if func_name == 'print':
            self.do_print(args)
        elif func_name == 'inputi':
            self.do_inputi(args)
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {func_name} undefined")

    # Handles user input (integer)
    def do_inputi(self, args):
        if args is None:
            args = []

        # Needs to be separate if statement
        if len(args) == 1:
            prompt = self.evaluate_expression(args[0])
            super().output(str(prompt))
        elif len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "No inputi() function found that takes > 1 parameter")
        # Else would be no args, which is valid and nothing needs to happen
    
        input = super().get_input()
        return int(input)
    
    # Handles printing
    def do_print(self, args):
        if args is None:
            args = []
        # Go through list of args and add to list
        all_args = []
        for arg in args:
            value = self.evaluate_expression(arg)
            all_args.append(str(value))
        # Print all args together
        result = ''.join(all_args)
        super().output(result)


    # Expression Nodes
    def evaluate_expression(self, expression_node):
        # Pseudocode
        # Value
        if expression_node.elem_type in [InterpreterBase.INT_NODE, InterpreterBase.STRING_NODE]:
            return self.get_value(expression_node)
        # Variable
        elif expression_node.elem_type == InterpreterBase.QUALIFIED_NAME_NODE:
            return self.get_value_of_variable(expression_node)
        # Operator
        elif expression_node.elem_type in ['+', '-', '*', '/']:
            return self.binary_operator(expression_node)
        # Function call
        elif expression_node.elem_type == InterpreterBase.FCALL_NODE:
            return self.function_call(expression_node)
        else:
            super().error(ErrorType.TYPE_ERROR, f"Unknown expression type: {expression_node.elem_type}")
    
    # Handles arithmetic
    def binary_operator(self, expression_node):
        op = expression_node.elem_type
        # This splits the expression into two, then runs eval on both parts
        # If both parts are binary operations in of themselves it basically recursively runs
        # So (5 + 7) - (10 - 4) -> op1 = 5 + 7, op2 -> 10 - 4
        # Then evaluate_expression calls binary_operator again on both ops and we get:
        # op1 = 5, op2 = 7; op1 = 10, op2 = 4
        # So 5 + 7 and 10 - 4 will be evaluated, then it'll subtract them
        op1 = self.evaluate_expression(expression_node.get('op1'))
        op2 = self.evaluate_expression(expression_node.get('op2'))
        
        if not isinstance(op1, int) or not isinstance(op2, int):
            super().error(ErrorType.TYPE_ERROR, "Incompatible types for arithmetic operation")
        
        if op == '+':
            return op1 + op2
        elif op == '-':
            return op1 - op2
        # Extra multiplication + division for next project?
        elif op == '*':
            return op1 * op2
        elif op == '/':
            if op2 == 0:
                # Not really a fault error, but didn't want to change intbase to add new error type in case that messes with grading
                super().error(ErrorType.FAULT_ERROR, "Cannot divide by 0. Fool.")
            return op1 / op2
        else:
            super().error(ErrorType.TYPE_ERROR, f"Unsupported operator: {op}")

    # Function call
    def function_call(self, expression_node):
        func_name = expression_node.get('name')
        args = expression_node.get('args')
        
        # Can only be input for this
        if func_name == 'inputi':
            return self.do_inputi(args)
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {func_name} undefined")

    # Variable Expression
    def get_value_of_variable(self, expression_node):
        var_name = expression_node.get('name')
        # Can't read an unassigned var
        if not var_name in self.variable_name_to_value:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} undefined")
        return self.variable_name_to_value[var_name]

    # Value Nodes
    def get_value(self, expression_node):
        return expression_node.get('val')
