"""
Simple Test Parser for Khamseena Programming Language
Academic project - basic tests only
"""

from scanner import Scanner
from khamseena_parser import Parser, ParseError, print_ast


def test_simple_examples():
    """Test basic parsing examples"""
    
    tests = [
        # Test 1: Simple function
        """
recipe main() {
    count x = 5;
    serve x;
    deliver 0;
}
        """,
        
        # Test 2: Function with parameters
        """
recipe add(count a, count b) {
    count result = a + b;
    deliver result;
}
        """,
        
        # Test 3: If statement
        """
count age = 18;
taste (age > 16) {
    serve "Adult";
} retaste {
    serve "Minor";
}
        """,
        
        # Test 4: While loop
        """
count i = 0;
stir (i < 5) {
    serve i;
    i = i + 1;
}
        """,
        
        # Test 5: Expressions
        """
count result = (5 + 3) * 2;
flavor flag = sweet;
        """
    ]
    
    for i, code in enumerate(tests, 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}")
        print('='*50)
        print("Code:")
        print(code.strip())
        print("\nParsing...")
        
        try:
            # Scan
            scanner = Scanner(code)
            tokens = scanner.tokenize()
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            print("✓ Success! AST:")
            print_ast(ast)
            
        except Exception as e:
            print(f"✗ Error: {e}")


def test_file(filename):
    """Test parsing a file"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        print(f"\nTesting file: {filename}")
        print("="*50)
        print("Code:")
        print(code)
        print("\nParsing...")
        
        # Scan
        scanner = Scanner(code)
        tokens = scanner.tokenize()
        print(f"Tokens: {len(tokens)}")
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        print("✓ Success! AST:")
        print_ast(ast)
        
    except FileNotFoundError:
        print(f"File {filename} not found")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific file
        test_file(sys.argv[1])
    else:
        # Run all tests
        print("KHAMSEENA PARSER - SIMPLE TESTS")
        test_simple_examples()
        
        # Test the example file if it exists
        try:
            test_file("examples/test.kh")
        except:
            pass