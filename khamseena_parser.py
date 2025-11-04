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

    # ---------- Utility functions ----------

    def peek(self):
        """Return current token without consuming"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def previous(self):
        """Return most recently consumed token"""
        if self.current > 0:
            return self.tokens[self.current - 1]
        return None

    def at_end(self):
        """Check if we've reached EOF"""
        token = self.peek()
        return token is None or token.type == TokenType.EOF

    def advance(self):
        """Consume current token and return it"""
        if not self.at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type):
        """Check if current token matches without consuming"""
        token = self.peek()
        return token is not None and token.type == token_type

    def match(self, *types):
        """Consume token if matches one of the given types"""
        if self.peek() and self.peek().type in types:
            self.advance()
            return True
        return False

    def consume(self, token_type, message):
        """Consume expected token or raise error"""
        if not self.check(token_type):
            self.error(message)
        return self.advance()

    def error(self, message):
        """Raise parse error with current token info"""
        token = self.peek()
        if token:
            raise ParseError(f"Parse error at line {token.line}: {message}")
        else:
            raise ParseError(f"Parse error: {message}")

    def check_semicolon_after_statement(self, stmt_type):
        """Check if semicolon is required after statement type"""
        if not self.check(TokenType.SEMICOLON):
            self.error(f"Expected ';' after {stmt_type}")

    def validate_parentheses(self, expected_type, context):
        """Validate that required parentheses are present"""
        if not self.check(expected_type):
            paren_name = "(" if expected_type == TokenType.LPAREN else ")"
            self.error(f"Expected '{paren_name}' in {context}")

    def validate_braces(self, expected_type, context):
        """Validate that required braces are present"""
        if not self.check(expected_type):
            brace_name = "{" if expected_type == TokenType.LBRACE else "}"
            self.error(f"Expected '{brace_name}' in {context}")

    # ---------- Parsing starts here ----------

    def parse(self):
        """Parse tokens into AST"""
        statements = []
        while not self.at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
        """Parse a statement"""
        try:
            if self.match(TokenType.FETCH):
                return self.parse_fetch()
            elif self.match(TokenType.RECIPE):
                return self.parse_function()
            elif self.match(TokenType.COUNT, TokenType.MEASURE, TokenType.NOTE, TokenType.FLAVOR):
                return self.parse_var_declaration()
            elif self.match(TokenType.SERVE):
                return self.parse_print()
            elif self.match(TokenType.POUR):
                return self.parse_input()
            elif self.match(TokenType.TASTE):
                return self.parse_if()
            elif self.match(TokenType.STIR):
                return self.parse_while()
            elif self.match(TokenType.DELIVER):
                return self.parse_return()
            elif self.match(TokenType.COMMENT):
                return self.parse_comment()
            elif self.match(TokenType.LBRACE):
                return self.parse_block()
            elif self.match(TokenType.IDENTIFIER):
                # Peek ahead: is it an assignment or expression?
                if self.check(TokenType.ASSIGN):
                    return self.parse_assignment()
                else:
                    expr = Variable(self.previous().value)
                    self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
                    return ExpressionStatement(expr)
            else:
                # Skip unknown tokens
                self.advance()
                return None
        except ParseError as e:
            print(f"⚠️ Warning: {e}")
            self.synchronize()
            return None

    # ---------- Statement types ----------

    def parse_function(self):
        """Parse function definition: recipe name(params) { body }"""
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value
        
        self.validate_parentheses(TokenType.LPAREN, "function parameters")
        self.consume(TokenType.LPAREN, "Expected '(' after function name")

        parameters = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                parameters.append(self.parse_parameter())

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        self.validate_braces(TokenType.LBRACE, "function body")
        self.consume(TokenType.LBRACE, "Expected '{' before function body")
        body = self.parse_block()
        return FunctionDef(name, parameters, body)

    def parse_parameter(self):
        """Parse function parameter: type name"""
        param_type = None
        if self.match(TokenType.COUNT, TokenType.MEASURE, TokenType.FLAVOR):
            param_type = self.previous().value
        name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
        return Parameter(param_type, name)

    def parse_var_declaration(self):
        """Parse variable declaration: type name [= expr];"""
        var_type = self.previous().value
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value
        var_line = name_token.line  # Capture line number here

        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        # Check for semicolon and report error with correct line number
        if not self.check(TokenType.SEMICOLON):
            raise ParseError(f"Parse error at line {var_line}: Expected ';' after variable declaration")
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDeclaration(var_type, name, initializer)

    def parse_assignment(self):
        """Parse assignment: name = expr;"""
        name = self.previous().value
        name_line = self.previous().line  # Capture line number
        
        self.consume(TokenType.ASSIGN, "Expected '=' in assignment")
        value = self.parse_expression()
        
        # Check for semicolon with correct line number
        if not self.check(TokenType.SEMICOLON):
            raise ParseError(f"Parse error at line {name_line}: Expected ';' after assignment")
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")
        return Assignment(name, value)

    def parse_print(self):
        """Parse print statement: serve expr;"""
        serve_line = self.previous().line  # Capture line number
        expr = self.parse_expression()
        
        # Check for semicolon with correct line number
        if not self.check(TokenType.SEMICOLON):
            raise ParseError(f"Parse error at line {serve_line}: Expected ';' after print statement")
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after print")
        return PrintStatement(expr)

    def parse_if(self):
        """Parse if statement: taste (expr) stmt [retaste stmt]"""
        self.validate_parentheses(TokenType.LPAREN, "taste statement")
        self.consume(TokenType.LPAREN, "Expected '(' after 'taste'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after taste condition")
        
        # Validate that we have a block starting with {
        self.validate_braces(TokenType.LBRACE, "taste statement body")
        then_stmt = self.parse_statement()

        else_stmt = None
        if self.match(TokenType.RETASTE):
            # Validate that retaste also has proper block structure
            self.validate_braces(TokenType.LBRACE, "retaste statement body")
            else_stmt = self.parse_statement()

        return IfStatement(condition, then_stmt, else_stmt)

    def parse_while(self):
        """Parse while statement: stir (expr) stmt"""
        self.validate_parentheses(TokenType.LPAREN, "stir statement")
        self.consume(TokenType.LPAREN, "Expected '(' after 'stir'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after stir condition")
        
        # Validate that we have a block starting with {
        self.validate_braces(TokenType.LBRACE, "stir statement body")
        body = self.parse_statement()
        return WhileStatement(condition, body)

    def parse_return(self):
        """Parse return statement: deliver [expr];"""
        return_line = self.previous().line  # Capture line number
        
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.parse_expression()
        
        # Check for semicolon with correct line number
        if not self.check(TokenType.SEMICOLON):
            raise ParseError(f"Parse error at line {return_line}: Expected ';' after return statement")
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ReturnStatement(value)

    def parse_block(self):
        """Parse block: { statements } - assumes { already consumed"""
        statements = []
        while not self.check(TokenType.RBRACE) and not self.at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.consume(TokenType.RBRACE, "Expected '}'")
        return Block(statements)

    def parse_comment(self):
        """Parse comment statement"""
        comment_text = self.previous().value
        return CommentStatement(comment_text)

    def parse_input(self):
        """Parse input statement: pour expr;"""
        pour_line = self.previous().line  # Capture line number
        expr = self.parse_expression()
        
        # Check for semicolon with correct line number
        if not self.check(TokenType.SEMICOLON):
            raise ParseError(f"Parse error at line {pour_line}: Expected ';' after input statement")
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after input")
        return InputStatement(expr)

    def parse_fetch(self):
        """Parse fetch statement: fetch identifier;"""
        name = self.consume(TokenType.IDENTIFIER, "Expected module name after 'fetch'")
        fetch_line = name.line
        
        # Check for semicolon with correct line number
        if not self.check(TokenType.SEMICOLON):
            raise ParseError(f"Parse error at line {fetch_line}: Expected ';' after fetch statement")
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after fetch statement")
        return FetchStatement(name.value)

    # ---------- Expressions ----------

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        expr = self.parse_and()
        while self.match(TokenType.OR):
            op = self.previous().value
            right = self.parse_and()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_and(self):
        expr = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.previous().value
            right = self.parse_equality()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_equality(self):
        expr = self.parse_comparison()
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.previous().value
            right = self.parse_comparison()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        while self.match(TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            op = self.previous().value
            right = self.parse_term()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous().value
            right = self.parse_factor()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.previous().value
            right = self.parse_unary()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.previous().value
            right = self.parse_unary()
            return UnaryOp(op, right)
        return self.parse_call()

    def parse_call(self):
        expr = self.parse_primary()
        if self.match(TokenType.LPAREN):
            args = []
            if not self.check(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    args.append(self.parse_expression())
            self.consume(TokenType.RPAREN, "Expected ')' after arguments")
            if isinstance(expr, Variable):
                return FunctionCall(expr.name, args)
            self.error("Can only call functions")
        return expr

    def parse_primary(self):
        if self.match(TokenType.INTEGER):
            return Literal(self.previous().value, "INTEGER")
        if self.match(TokenType.FLOAT):
            return Literal(self.previous().value, "FLOAT")
        if self.match(TokenType.STRING):
            return Literal(self.previous().value, "STRING")
        if self.match(TokenType.SWEET):
            return Literal("sweet", "BOOLEAN")
        if self.match(TokenType.SOUR):
            return Literal("sour", "BOOLEAN")
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous().value)
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        self.error("Expected expression")

    def synchronize(self):
        """Skip tokens until next valid statement"""
        self.advance()
        while not self.at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in (TokenType.RECIPE, TokenType.SERVE, TokenType.COUNT):
                return
            self.advance()


def get_expression_summary(node):
    """Get a concise summary of an expression for variable declarations only"""
    if isinstance(node, Literal):
        return f"EXP({node.value})"
    elif isinstance(node, Variable):
        return f"EXP({node.name})"
    elif isinstance(node, BinaryOp):
        left_summary = get_expression_summary(node.left)
        right_summary = get_expression_summary(node.right)
        return f"EXP({left_summary} {node.operator} {right_summary})"
    elif isinstance(node, UnaryOp):
        operand_summary = get_expression_summary(node.operand)
        return f"EXP({node.operator}{operand_summary})"
    elif isinstance(node, FunctionCall):
        return f"EXP(CALL {node.name})"
    else:
        return "EXP"


def print_ast(node, indent=0):
    """Simple AST printer for debugging"""
    spaces = "  " * indent
    
    # Special handling only for VarDeclaration
    if isinstance(node, VarDeclaration):
        # Map token types to readable names
        type_map = {
            'count': 'INTEGER',
            'measure': 'FLOAT',
            'note': 'STRING',
            'flavor': 'BOOLEAN'
        }
        var_type = type_map.get(node.var_type, node.var_type.upper())
        
        if node.initializer:
            expr_summary = get_expression_summary(node.initializer)
            print(f"{spaces}{var_type} identifier {node.name} = {expr_summary}")
        else:
            print(f"{spaces}{var_type} identifier {node.name}")
        return  # Don't process children for VarDeclaration
    
    # Default behavior for all other nodes
    print(f"{spaces}{node}")

    if hasattr(node, 'statements'):
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    elif isinstance(node, ExpressionStatement):
        print(f"{spaces}  Expression:")
        print_ast(node.expression, indent + 2)
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
    elif hasattr(node, 'value') and node.value:  # Add this for assignments
        print(f"{spaces}  value:")
        print_ast(node.value, indent + 2)
    elif hasattr(node, 'initializer') and node.initializer:  # Add this for var declarations
        print_ast(node.initializer, indent + 2)
    elif hasattr(node, 'left'):
        print(f"{spaces}  left:")
        print_ast(node.left, indent + 2)
        print(f"{spaces}  right:")
        print_ast(node.right, indent + 2)