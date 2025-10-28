"""
Token class for Khamseena Programming Language
Represents a lexical token with type, value, and position information
"""

class TokenType:
    """Token type constants for Khamseena language"""
    
    # Keywords
    BREW = "BREW"
    RECIPE = "RECIPE"
    COUNT = "COUNT"
    MEASURE = "MEASURE"
    NOTE = "NOTE"  
    FLAVOR = "FLAVOR"  
    SWEET = "SWEET"  
    SOUR = "SOUR"  
    SERVE = "SERVE"
    POUR = "POUR"
    TASTE = "TASTE"
    RETASTE = "RETASTE" 
    STIR = "STIR"
    MIX = "MIX"
    STOP = "STOP"  
    SKIP = "SKIP"  
    DELIVER = "DELIVER"
    FETCH = "FETCH"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    ASSIGN = "ASSIGN"
    
    # Comparison Operators
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    
    # Logical Operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    
    # Literals
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    
    # Special
    EOF = "EOF"
    COMMENT = "COMMENT"


class Token:
    """Represents a single token in the source code"""
    
    def __init__(self, token_type, value, line, column):
        """
        Initialize a token
        
        Args:
            token_type: Type of token (from TokenType class)
            value: Actual string value from source code
            line: Line number where token appears
            column: Column number where token starts
        """
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        """String representation for debugging"""
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"
    
    def __str__(self):
        """User-friendly string representation"""
        return f"<{self.type}: '{self.value}' at {self.line}:{self.column}>"
    
    def __eq__(self, other):
        """Check equality based on type and value"""
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value


# Keyword mapping for easy lookup
KEYWORDS = {
    "brew": TokenType.BREW,
    "recipe": TokenType.RECIPE,
    "count": TokenType.COUNT,
    "measure": TokenType.MEASURE,
    "note": TokenType.NOTE,  
    "flavor": TokenType.FLAVOR,  
    "sweet": TokenType.SWEET, 
    "sour": TokenType.SOUR,  
    "serve": TokenType.SERVE,
    "pour": TokenType.POUR,
    "taste": TokenType.TASTE,
    "retaste": TokenType.RETASTE,  
    "stir": TokenType.STIR,
    "mix": TokenType.MIX,
    "stop": TokenType.STOP, 
    "skip": TokenType.SKIP, 
    "deliver": TokenType.DELIVER,
    "fetch": TokenType.FETCH,
}