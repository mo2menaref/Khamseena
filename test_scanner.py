"""
Unit tests for Khamseena Scanner
Run with: python test_scanner.py
"""

import unittest
from scanner import Scanner, LexicalError
from khamseena_token import Token, TokenType


class TestScanner(unittest.TestCase):
    """Test cases for the Khamseena scanner"""
    
    def test_keywords(self):
        """Test recognition of all keywords"""
        source = "brew recipe count measure note flavor sweet sour serve pour taste retaste stir mix stop skip deliver fetch"  # Line 17 - updated keyword list
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        expected_types = [
            TokenType.BREW, TokenType.RECIPE, TokenType.COUNT, TokenType.MEASURE,
            TokenType.NOTE, TokenType.FLAVOR, TokenType.SWEET, TokenType.SOUR,  
            TokenType.SERVE, TokenType.POUR, TokenType.TASTE, TokenType.RETASTE, 
            TokenType.STIR, TokenType.MIX, TokenType.STOP, TokenType.SKIP,  
            TokenType.DELIVER, TokenType.FETCH, TokenType.EOF
        ]
        
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_identifiers(self):
        """Test identifier recognition"""
        source = "myVar _test var123 camelCase"
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "myVar")
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "_test")
        self.assertEqual(tokens[2].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].value, "var123")
    
    def test_integers(self):
        """Test integer literal recognition"""
        source = "0 10 255 1000"
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[0].value, "0")
        self.assertEqual(tokens[1].type, TokenType.INTEGER)
        self.assertEqual(tokens[1].value, "10")
        self.assertEqual(tokens[3].type, TokenType.INTEGER)
        self.assertEqual(tokens[3].value, "1000")
    
    def test_floats(self):
        """Test float literal recognition"""
        source = "3.14 0.5 23.5"
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.FLOAT)
        self.assertEqual(tokens[0].value, "3.14")
        self.assertEqual(tokens[1].type, TokenType.FLOAT)
        self.assertEqual(tokens[1].value, "0.5")
    
    def test_strings(self):
        """Test string literal recognition"""
        source = '"hello" "world" "Hello, World!"'
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, '"hello"')
        self.assertEqual(tokens[2].type, TokenType.STRING)
        self.assertEqual(tokens[2].value, '"Hello, World!"')
    
    def test_string_escape_sequences(self):
        """Test string escape sequences"""
        source = r'"line1\nline2" "tab\there"'
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.STRING)
    
    def test_operators(self):
        """Test operator recognition"""
        source = "+ - * / % = == != > < >= <= && || !"
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.MODULO, TokenType.ASSIGN, TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL,
            TokenType.AND, TokenType.OR, TokenType.NOT, TokenType.EOF
        ]
        
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_delimiters(self):
        """Test delimiter recognition"""
        source = "( ) { } ; ,"
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        expected_types = [
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.SEMICOLON, TokenType.COMMA, TokenType.EOF
        ]
        
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_comments(self):
        """Test that comments are ignored"""
        source = """count x = 10; # This is a comment
        # Another comment
        count y = 20;"""
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        # Should only have tokens for the actual code, not comments
        self.assertEqual(tokens[0].type, TokenType.COUNT)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "x")
    
    def test_whitespace_handling(self):
        """Test that whitespace is properly ignored"""
        source = "count    x   =   10  ;  "
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(len(tokens), 6)  # count, x, =, 10, ;, EOF
    
    def test_simple_program(self):
        """Test scanning a simple complete program"""
        source = """fetch basics
        
recipe brew() {
    count age = 25;
    serve "Age: " + age;
    deliver 0;
}"""
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        # Check first few tokens
        self.assertEqual(tokens[0].type, TokenType.FETCH)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "basics")
        self.assertEqual(tokens[2].type, TokenType.RECIPE)
    
    def test_conditional_statement(self):
        """Test scanning if-else structure"""
        source = """taste (grade >= 50) {
    serve "Pass";
}
refill {
    serve "Fail";
}"""
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.TASTE)
        self.assertEqual(tokens[1].type, TokenType.LPAREN)
    
    def test_loop_statement(self):
        """Test scanning loop structure"""
        source = """stir (counter < 5) {
    serve counter;
    counter = counter + 1;
}"""
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.STIR)
    
    def test_position_tracking(self):
        """Test that line and column numbers are tracked correctly"""
        source = """count x = 10;
count y = 20;"""
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        # First token should be on line 1
        self.assertEqual(tokens[0].line, 1)
        # Token on second line
        self.assertEqual(tokens[5].line, 2)
    
    def test_error_invalid_character(self):
        """Test error handling for invalid characters"""
        source = "count x = 10 @ ;"
        scanner = Scanner(source)
        
        with self.assertRaises(LexicalError):
            scanner.tokenize()
    
    def test_error_unterminated_string(self):
        """Test error handling for unterminated strings"""
        source = 'count x = "unterminated;'
        scanner = Scanner(source)
        
        with self.assertRaises(LexicalError):
            scanner.tokenize()
    
    def test_function_with_parameters(self):
        """Test scanning function definition with parameters"""
        source = """recipe add(count a, count b) {
    count result = a + b;
    deliver result;
}"""
        scanner = Scanner(source)
        tokens = scanner.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.RECIPE)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "add")
        self.assertEqual(tokens[2].type, TokenType.LPAREN)


def run_tests():
    """Run all tests and display results"""
    print("\n" + "="*70)
    print("KHAMSEENA SCANNER - UNIT TESTS")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestScanner)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)