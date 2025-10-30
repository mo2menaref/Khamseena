"""
Simple Parser for Khamseena Programming Language
Academic project - basic recursive descent parser
"""

from khamseena_token import Token, TokenType
from ast_nodes import *


class ParseError(Exception):
    """Exception for parsing errors"""
    pass


class Parser:
    """Simple recursive descent parser"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
    
    def error(self, message):
        """Raise parse error with current token info"""
        token = self.tokens[self.current] if self.current < len(self.tokens) else None
        if token:
            raise ParseError(f"Parse error at line {token.line}: {message}")
        else:
            raise ParseError(f"Parse error: {message}")
    
    def peek(self):
        """Get current token without consuming it"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None
    
    def advance(self):
        """Move to next token"""
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return self.peek()
    
    def match(self, *types):
        """Check if current token matches any given type"""
        token = self.peek()
        return token and token.type in types
    
    def consume(self, token_type, message):
        """Consume token of expected type or error"""
        token = self.peek()
        if not token or token.type != token_type:
            self.error(message)
        self.advance()
        return token
    
    def parse(self):
        """Parse tokens into AST"""
        statements = []
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)
    
    def parse_statement(self):
        """Parse a statement"""
        try:
            if self.match(TokenType.RECIPE):
                return self.parse_function()
            elif self.match(TokenType.COUNT, TokenType.MEASURE, TokenType.FLAVOR):
                return self.parse_var_declaration()
            elif self.match(TokenType.SERVE):
                return self.parse_print()
            elif self.match(TokenType.TASTE):
                return self.parse_if()
            elif self.match(TokenType.STIR):
                return self.parse_while()
            elif self.match(TokenType.DELIVER):
                return self.parse_return()
            elif self.match(TokenType.LBRACE):
                return self.parse_block()
            elif self.match(TokenType.IDENTIFIER):
                return self.parse_assignment()
            else:
                # Skip unknown tokens
                self.advance()
                return None
        except ParseError as e:
            print(f"Warning: {e}")
            self.synchronize()
            return None
    
    def parse_function(self):
        """Parse function definition: recipe name(params) { body }"""
        self.consume(TokenType.RECIPE, "Expected 'recipe'")
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value
        
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        
        # Parse parameters
        parameters = []
        if not self.match(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.parse_parameter())
        
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        body = self.parse_block()
        
        return FunctionDef(name, parameters, body)
    
    def parse_parameter(self):
        """Parse function parameter: type name"""
        param_type = self.consume(TokenType.COUNT, "Expected parameter type").value
        if self.match(TokenType.MEASURE, TokenType.FLAVOR):
            param_type = self.advance().value
        name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
        return Parameter(param_type, name)
    
    def parse_var_declaration(self):
        """Parse variable declaration: type name [= expr];"""
        var_type = self.advance().value  # consume type
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDeclaration(var_type, name, initializer)
    
    def parse_assignment(self):
        """Parse assignment: name = expr;"""
        name = self.advance().value  # consume identifier
        self.consume(TokenType.ASSIGN, "Expected '=' in assignment")
        value = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")
        return Assignment(name, value)
    
    def parse_print(self):
        """Parse print statement: serve expr;"""
        self.consume(TokenType.SERVE, "Expected 'serve'")
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after print")
        return PrintStatement(expr)
    
    def parse_if(self):
        """Parse if statement: taste (expr) stmt [retaste stmt]"""
        self.consume(TokenType.TASTE, "Expected 'taste'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'taste'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")
        
        then_stmt = self.parse_statement()
        
        else_stmt = None
        if self.match(TokenType.RETASTE):
            self.advance()
            else_stmt = self.parse_statement()
        
        return IfStatement(condition, then_stmt, else_stmt)
    
    def parse_while(self):
        """Parse while statement: stir (expr) stmt"""
        self.consume(TokenType.STIR, "Expected 'stir'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'stir'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")
        body = self.parse_statement()
        return WhileStatement(condition, body)
    
    def parse_return(self):
        """Parse return statement: deliver [expr];"""
        self.consume(TokenType.DELIVER, "Expected 'deliver'")
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ReturnStatement(value)
    
    def parse_block(self):
        """Parse block: { statements }"""
        self.consume(TokenType.LBRACE, "Expected '{'")
        statements = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.consume(TokenType.RBRACE, "Expected '}'")
        return Block(statements)
    
    def parse_expression(self):
        """Parse expression with operator precedence"""
        return self.parse_or()
    
    def parse_or(self):
        """Parse logical OR"""
        expr = self.parse_and()
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.parse_and()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_and(self):
        """Parse logical AND"""
        expr = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_equality(self):
        """Parse equality operators"""
        expr = self.parse_comparison()
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.advance().value
            right = self.parse_comparison()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_comparison(self):
        """Parse comparison operators"""
        expr = self.parse_term()
        while self.match(TokenType.GREATER, TokenType.LESS, 
                         TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            op = self.advance().value
            right = self.parse_term()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_term(self):
        """Parse addition and subtraction"""
        expr = self.parse_factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_factor()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_factor(self):
        """Parse multiplication and division"""
        expr = self.parse_unary()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_unary()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_unary(self):
        """Parse unary operators"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance().value
            expr = self.parse_unary()
            return UnaryOp(op, expr)
        return self.parse_call()
    
    def parse_call(self):
        """Parse function calls"""
        expr = self.parse_primary()
        
        if self.match(TokenType.LPAREN):
            self.advance()
            args = []
            if not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    args.append(self.parse_expression())
            self.consume(TokenType.RPAREN, "Expected ')' after arguments")
            
            if isinstance(expr, Variable):
                return FunctionCall(expr.name, args)
            else:
                self.error("Can only call functions")
        
        return expr
    
    def parse_primary(self):
        """Parse primary expressions"""
        if self.match(TokenType.INTEGER):
            return Literal(self.advance().value, "INTEGER")
        
        if self.match(TokenType.FLOAT):
            return Literal(self.advance().value, "FLOAT")
        
        if self.match(TokenType.STRING):
            return Literal(self.advance().value, "STRING")
        
        if self.match(TokenType.SWEET):
            self.advance()
            return Literal("sweet", "BOOLEAN")
        
        if self.match(TokenType.SOUR):
            self.advance()
            return Literal("sour", "BOOLEAN")
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.advance().value)
        
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        self.error("Expected expression")
    
    def synchronize(self):
        """Skip tokens until next statement"""
        self.advance()
        while not self.match(TokenType.EOF):
            if self.tokens[self.current - 1].type == TokenType.SEMICOLON:
                return
            if self.match(TokenType.RECIPE, TokenType.COUNT, TokenType.SERVE):
                return
            self.advance()


def print_ast(node, indent=0):
    """Simple AST printer for debugging"""
    spaces = "  " * indent
    print(f"{spaces}{node}")
    
    # Print children
    if hasattr(node, 'statements'):
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    elif hasattr(node, 'body') and node.body:
        print_ast(node.body, indent + 1)
    elif hasattr(node, 'condition'):
        print(f"{spaces}  condition:")
        print_ast(node.condition, indent + 2)
        if hasattr(node, 'then_stmt'):
            print(f"{spaces}  then:")
            print_ast(node.then_stmt, indent + 2)
        if hasattr(node, 'else_stmt') and node.else_stmt:
            print(f"{spaces}  else:")
            print_ast(node.else_stmt, indent + 2)
    elif hasattr(node, 'left'):
        print(f"{spaces}  left:")
        print_ast(node.left, indent + 2)
        print(f"{spaces}  right:")
        print_ast(node.right, indent + 2)