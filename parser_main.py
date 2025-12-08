import sys
import os
from scanner import Scanner
from khamseena_parser import Parser, ParseError, print_ast
from semantic_analyzer import SemanticAnalyzer

def main():
    """Simple main function"""
    
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python parser_main.py <file.kh>   - Parse a file")
        print("  python parser_main.py test        - Run tests")
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
        print("\n1. Scanning...")
        scanner = Scanner(code)
        tokens = scanner.tokenize()
        print(f"   Found {len(tokens)} tokens")
        
        # Parse
        print("\n2. Parsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✓ Parse successful!")
        
        print("\n3. Abstract Syntax Tree:")
        print("-"*40)
        print_ast(ast)
        
        # Semantic Analysis
        print("\n4. Semantic Analysis...")
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)
        
        if not success:
            print("\n⚠️  Program has semantic errors!")
            sys.exit(1)
        else:
            print("\n🎉 Program is semantically correct!")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()