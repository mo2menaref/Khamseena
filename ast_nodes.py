class ASTNode:
    """Base class for all AST nodes"""
    def __init__(self):
        pass

# Program structure
class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    
    def __str__(self):
        return f"Program({len(self.statements)} statements)"

class ExpressionStatement:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStatement({self.expression})"

class FunctionDef:
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body
    
    def __str__(self):
        # Change this to customize function definitions
        return f"FUNCTION {self.name}"
        # Alternative: return f"Function Definition: {self.name}"

class Parameter(ASTNode):
    def __init__(self, param_type, name):
        self.param_type = param_type
        self.name = name
    
    def __str__(self):
        return f"Param({self.param_type} {self.name})"

class VarDeclaration(ASTNode):
    def __init__(self, var_type, name, initializer=None):
        self.var_type = var_type
        self.name = name
        self.initializer = initializer
    
    def __str__(self):
        # Change this method to get your desired output format
        type_map = {
            'count': 'INTEGER',
            'measure': 'FLOAT', 
            'note': 'STRING',
            'flavor': 'BOOLEAN'
        }
        mapped_type = type_map.get(self.var_type, self.var_type.upper())
        return f"{mapped_type} identifier {self.name}"

class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        # Show both variable name and what's being assigned
        return f"Assignment to identifier {self.name}"

class PrintStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return "Print"

class IfStatement(ASTNode):
    def __init__(self, condition, then_stmt, else_stmt=None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt
    
    def __str__(self):
        return f"If(has_else={self.else_stmt is not None})"

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def __str__(self):
        return "While"

class ReturnStatement(ASTNode):
    def __init__(self, value=None):
        self.value = value
    
    def __str__(self):
        return "Return"

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    
    def __str__(self):
        return f"Block({len(self.statements)} stmts)"

class BinaryOp:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        # Change this to customize binary operations
        return f"BinaryOp({self.operator})"
        # Alternative: return f"Operation: {self.operator}"

class UnaryOp(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
    
    def __str__(self):
        return f"UnaryOp({self.operator})"

class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
    
    def __str__(self):
        return f"Call({self.name}, {len(self.arguments)} args)"

class Variable:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        # Change this to customize variable references
        return f"identifier {self.name}"
        # Alternative: return f"Variable({self.name})"

class Literal:
    def __init__(self, value, literal_type):
        self.value = value
        self.type = literal_type
    
    def __str__(self):
        # Change this to customize literal display
        return f"{self.type} {self.value}"
        # Alternative: return f"Literal({self.type}: {self.value})"

class CommentStatement(ASTNode):
    def __init__(self, text):
        self.text = text
    
    def __str__(self):
        return f"Comment: {self.text}"

class InputStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return "Input"

