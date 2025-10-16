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
                    
        return None

    def run_func(self, func_node):
        # Also mostly copied from pseudocode, added evaluate for no statements
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
    
    # Check variable name
    def var_name_exists(self, var_name):
        return var_name in self.variable_name_to_value

    # Get variable name
    def get_target_variable_name(self, statement_node):
        return statement_node.get('var')
        
    # Variable Definition Statement
    def do_definition(self, statement_node):
        var_name = statement_node.get('name')
        if self.var_name_exists(var_name):
            super().error(ErrorType.NAME_ERROR, f"Vairable {var_name} already defined")
        self.variable_name_to_value[var_name] = None
       
    # Assignemnt Statement
    def do_assignment(self, statement_node):
        # Credit to pseudocode!
        var_name = self.get_target_variable_name(statement_node)
        if not self.var_name_exists(var_name):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not defined")
        source_node = statement_node.get('expression')
        val = self.evaluate_expression(source_node)
        self.variable_name_to_value[var_name] = val

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

    # Handles user input
    def do_inputi(self, args):
        if args is None:
            args = []
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "No inputi() function found that takes > 1 parameter")
        else:
            prompt = self.evaluate_expression(args[0])
            super().output(str(prompt))
    
        input = super().get_input()
        return int(input)
    
    # Handles printing
    def do_print(self, args):
        if args is None:
            args = []
        all_args = []
        for arg in args:
            value = self.evaluate_expression(arg)
            all_args.append(str(value))
        result = ''.join(all_args)
        super().output(result)


    # Expression Nodes
    def evaluate_expression(self, expression_node):
        # Pseudocode
        if expression_node.elem_type in [InterpreterBase.INT_NODE, InterpreterBase.STRING_NODE]:
            return self.get_value(expression_node)
        elif expression_node.elem_type == InterpreterBase.QUALIFIED_NAME_NODE:
            return self.get_value_of_variable(expression_node)
        elif expression_node.elem_type in ['+', '-', '*', '/']:
            return self.binary_operator(expression_node)
        elif expression_node.elem_type == InterpreterBase.FCALL_NODE:
            return self.function_call(expression_node)
        else:
            super().error(ErrorType.TYPE_ERROR, f"Unknown expression type: {expression_node.elem_type}")
    
    # Handles arithmetic
    def binary_operator(self, expression_node):
        op = expression_node.elem_type
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
            return op1 / op2
        else:
            super().error(ErrorType.TYPE_ERROR, f"Unsupported operator: {op}")

    # Function call
    def function_call(self, expression_node):
        func_name = expression_node.get('name')
        args = expression_node.get('args')
        
        # Can only be input for this
        if func_name == 'inputi':
            return self.execute_inputi(args)
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {func_name} undefined")

    # Variable Expression
    def get_value_of_variable(self, expression_node):
        var_name = expression_node.get('name')
        # Reading a declared-but-unassigned variable is an error
        if not self.var_name_exists(var_name):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} undefined")
        return self.variable_name_to_value[var_name]

    # Value Nodes
    def get_value(self, expression_node):
        return expression_node.get('val')
