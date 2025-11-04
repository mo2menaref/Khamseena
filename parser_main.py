
import sys
import os
from scanner import Scanner
from khamseena_parser import Parser, ParseError, print_ast

def main():
    """Simple main function"""
    
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py <file.kh>   - Parse a file")
        print("  python main.py test        - Run tests")
        return
    
    if sys.argv[1] == "test":
        from test_parser import test_simple_examples
        test_simple_examples()
        return
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        print(f"Parsing file: {filename}")
        print("="*40)
        print("Source code:")
        print(code)
        print("="*40)
        
        # Scan
        print("1. Scanning...")
        scanner = Scanner(code)
        tokens = scanner.tokenize()
        print(f"   Found {len(tokens)} tokens")
        
        # Parse
        print("2. Parsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✓ Parse successful!")
        
        print("\n3. Abstract Syntax Tree:")
        print("-"*40)
        print_ast(ast)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()