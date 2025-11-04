"""
Scanner/Lexical Analyzer for Khamseena Programming Language
Converts source code into a stream of tokens
"""

from khamseena_token import Token, TokenType, KEYWORDS

class LexicalError(Exception):
    """Exception raised for lexical analysis errors"""
    pass

class Scanner:
    """Lexical analyzer that tokenizes Khamseena source code"""
    
    def __init__(self, source):
        """
        Initialize the scanner with source code
        
        Args:
            source: String containing the source code to scan
        """
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source else None
        self.tokens = []
    
    def error(self, message):
        """
        Raise a lexical error with position information
        
        Args:
            message: Error description
        """
        raise LexicalError(f"Lexical Error at line {self.line}, column {self.column}: {message}")
    
    def advance(self):
        """Move to the next character in the source code"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        self.position += 1
        if self.position < len(self.source):
            self.current_char = self.source[self.position]
        else:
            self.current_char = None
    
    def peek(self, offset=1):
        """
        Look ahead at the next character(s) without consuming them
        
        Args:
            offset: How many characters to look ahead (default: 1)
        
        Returns:
            The character at position + offset, or None if out of bounds
        """
        peek_pos = self.position + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None
    
    def skip_whitespace(self):
        """Skip whitespace characters (space, tab, newline, carriage return)"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        """Capture single-line comments starting with #"""
        if self.current_char == '#':
            start_line = self.line
            start_column = self.column
            comment_text = ""
            
            # Read the entire comment including the #
            while self.current_char is not None and self.current_char != '\n':
                comment_text += self.current_char
                self.advance()
            
            # Create and add comment token
            self.tokens.append(Token(TokenType.COMMENT, comment_text, start_line, start_column))
            
            # Skip the newline character
            if self.current_char == '\n':
                self.advance()
    
    def read_number(self):
        """
        Read a numeric literal (integer or float)
        
        Returns:
            Token representing the number
        """
        start_line = self.line
        start_column = self.column
        num_str = ""
        is_float = False
        
        # Read digits before decimal point
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()
        
        # Check for decimal point
        if self.current_char == '.' and self.peek() is not None and self.peek().isdigit():
            is_float = True
            num_str += self.current_char
            self.advance()
            
            # Read digits after decimal point
            while self.current_char is not None and self.current_char.isdigit():
                num_str += self.current_char
                self.advance()
        
        # Determine token type
        token_type = TokenType.FLOAT if is_float else TokenType.INTEGER
        return Token(token_type, num_str, start_line, start_column)
    
    def read_string(self):
        """
        Read a string literal enclosed in double quotes
        
        Returns:
            Token representing the string
        """
        start_line = self.line
        start_column = self.column
        string_value = ""
        
        # Skip opening quote
        self.advance()
        
        # Read until closing quote or end of file
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\n':
                self.error("Unterminated string literal")
            
            # Handle escape sequences
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    self.error("Unterminated string literal")
                
                # Common escape sequences
                escape_chars = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"'
                }
                # "ramez   asham "
                if self.current_char in escape_chars:
                    string_value += escape_chars[self.current_char]
                else:
                    string_value += self.current_char
                
                self.advance()
            else:
                string_value += self.current_char
                self.advance()
        
        if self.current_char != '"':
            self.error("Unterminated string literal")
        
        # Skip closing quote
        self.advance()
        
        # Return the string WITH quotes (as it appears in source)
        return Token(TokenType.STRING, f'"{string_value}"', start_line, start_column)
    
    def read_identifier(self):
        """
        Read an identifier or keyword
        
        Returns:
            Token representing identifier or keyword
        """
        start_line = self.line
        start_column = self.column
        identifier = ""
        
        # Read alphanumeric characters and underscores
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            identifier += self.current_char
            self.advance()
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(identifier, TokenType.IDENTIFIER)
        return Token(token_type, identifier, start_line, start_column)
    
    def read_operator(self):
        """
        Read an operator (single or multi-character)
        
        Returns:
            Token representing the operator
        """
        start_line = self.line
        start_column = self.column
        char = self.current_char
        
        # Two-character operators
        if char == '=' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.EQUAL, "==", start_line, start_column)
        
        elif char == '!' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.NOT_EQUAL, "!=", start_line, start_column)
        
        elif char == '>' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.GREATER_EQUAL, ">=", start_line, start_column)
        
        elif char == '<' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.LESS_EQUAL, "<=", start_line, start_column)
        
        elif char == '&' and self.peek() == '&':
            self.advance()
            self.advance()
            return Token(TokenType.AND, "&&", start_line, start_column)
        
        elif char == '|' and self.peek() == '|':
            self.advance()
            self.advance()
            return Token(TokenType.OR, "||", start_line, start_column)
        
        # Single-character operators
        operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '=': TokenType.ASSIGN,
            '>': TokenType.GREATER,
            '<': TokenType.LESS,
            '!': TokenType.NOT,
        }
        
        if char in operators:
            token_type = operators[char]
            self.advance()
            return Token(token_type, char, start_line, start_column)
        
        return None
    
    def tokenize(self):
        """
        Main method to tokenize the entire source code
        
        Returns:
            List of tokens
        """
        self.tokens = []
        
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Skip comments
            if self.current_char == '#':
                self.skip_comment()
                continue
            
            # Save position for error reporting
            start_line = self.line
            start_column = self.column
            
            # Identifiers and keywords (start with letter or underscore)
            if self.current_char.isalpha() or self.current_char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Numbers (start with digit)
            if self.current_char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # String literals (start with double quote)
            if self.current_char == '"':
                self.tokens.append(self.read_string())
                continue
            
            # Operators
            operator_token = self.read_operator()
            if operator_token:
                self.tokens.append(operator_token)
                continue
            
            # Delimiters
            delimiters = {
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
            }
            
            if self.current_char in delimiters:
                token_type = delimiters[self.current_char]
                self.tokens.append(Token(token_type, self.current_char, start_line, start_column))
                self.advance()
                continue
            
            # If we reach here, it's an invalid character
            self.error(f"Invalid character '{self.current_char}'")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
    
    def print_tokens(self, output_file=None):
        """
        Print tokens in a readable format
        
        Args:
            output_file: Optional file path to write tokens to
        """
        output_lines = []
        output_lines.append("=" * 70)
        output_lines.append("KHAMSEENA SCANNER - TOKEN OUTPUT")
        output_lines.append("=" * 70)
        output_lines.append(f"Total Tokens: {len(self.tokens)}")
        output_lines.append("=" * 70)
        output_lines.append(f"{'TOKEN TYPE':<20} {'VALUE':<20} {'POSITION':<15}")
        output_lines.append("-" * 70)
        
        for token in self.tokens:
            line = f"{token.type:<20} {token.value:<20} {token.line}:{token.column}"
            output_lines.append(line)
        
        output_lines.append("=" * 70)
        
        output_text = "\n".join(output_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_text)
            print(f"Tokens written to {output_file}")
        else:
            print(output_text)