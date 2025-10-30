

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

# Statements
class FunctionDef(ASTNode):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters  # list of Parameter objects
        self.body = body  # Block
    
    def __str__(self):
        return f"Function({self.name}, {len(self.parameters)} params)"

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
        return f"VarDecl({self.var_type} {self.name})"

class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"Assign({self.name})"

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

# Expressions
class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"BinaryOp({self.operator})"

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

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Var({self.name})"

class Literal(ASTNode):
    def __init__(self, value, literal_type):
        self.value = value
        self.literal_type = literal_type
    
    def __str__(self):
        return f"Literal({self.literal_type}: {self.value})"